import os
import datetime
import numpy as np
import pandas as pd
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector
from agent import CreatureAgent, RESTING, FORAGING, RETURNING_LOADED, RETURNING_EMPTY
from cell_agent import cell_agent

class SwarmModel(Model):

    def __init__(self,
        # Environment
        width: int,
        height: int,
        creature_num: int,
        cluster_num: int,
        cluster_spread: float,
        food_coverage: float,
        # Temperature
        temperature_critical: float,
        heat_rate: float,
        # Movement
        speed_max: int,
        # ACO
        pheromone_deposit: float,
        evaporation_rate: float,
        exploration_weight: float
    ):
        super().__init__()
        # Energy
        self.energy_max: float          = 200.0
        self.energy_drain_base: float   = 0.3
        self.energy_drain_move: float   = 0.2
        self.energy_forage_min: float   = 40.0
        # Temperature
        self.temperature_safe: float    = 20.0
        self.temperature_critical       = temperature_critical
        self.cool_rate: float           = 1.5
        self.heat_rate                  = heat_rate
        self.heat_abort_ratio: float    = 0.75
        # Movement
        self.speed_max                  = speed_max
        self.momentum_weight: float     = 2.0
        self.outward_weight: float      = 0.1
        # ACO
        self.pheromone_deposit          = pheromone_deposit
        self.evaporation_rate           = evaporation_rate
        self.exploration_weight         = exploration_weight
        # Grid
        self.grid = OrthogonalMooreGrid([width, height], torus=False, capacity=creature_num+1)
        self.nest_location = (width // 2, height // 2)
        
        # Stats
        self.food_collected: float = 0.0
        self.dead_creatures: int = 0
        self.datacollector = DataCollector(
            model_reporters={
                "Food Collected":   lambda m: m.food_collected,
                "Average Energy":   lambda m: m.get_average_energy(),
                "Alive Creatures":  lambda m: sum(1 for a in m.agents_by_type[CreatureAgent] if a.alive),
                "Dead Creatures":   lambda m: m.dead_creatures,
                "Resting":          lambda m: sum(1 for a in m.agents_by_type[CreatureAgent] if a.alive and a.state == RESTING),
                "Foraging":         lambda m: sum(1 for a in m.agents_by_type[CreatureAgent] if a.alive and a.state == FORAGING),
                "Returning Loaded": lambda m: sum(1 for a in m.agents_by_type[CreatureAgent] if a.alive and a.state == RETURNING_LOADED),
                "Returning Empty":  lambda m: sum(1 for a in m.agents_by_type[CreatureAgent] if a.alive and a.state == RETURNING_EMPTY)
            }
        )

        # Create cell agents for each grid cell
        for cell in self.grid:
            ca = cell_agent(self, len(self.agents), cell)
            self.agents.add(ca)

        # Mark nest cell
        nest_ca = self._get_cell_agent(self.grid[self.nest_location])
        if nest_ca:
            nest_ca.is_nest = True

        # Seed food
        target_food_cells = int(width * height * food_coverage)
        cells_per_cluster = max(1, target_food_cells // cluster_num)
        nest_cx, nest_cy  = self.nest_location
        seeded_cells = set()
        cluster_distance_min: int = 10
        food_distance_min: int = 6
        clusters_placed: int = 0
        cluster_attempts: int = 0
        cluster_centers = []

        while clusters_placed < cluster_num and len(seeded_cells) < target_food_cells and cluster_attempts < 2000:
            cluster_attempts += 1
            cx = self.random.randint(0, width - 1)
            cy = self.random.randint(0, height - 1)
            if (abs(cx - nest_cx) < food_distance_min and abs(cy - nest_cy) < food_distance_min):
                continue
            # Stay at least cluster_distance_min away from existing cluster centers
            if (any(np.hypot(cx - px, cy - py) < cluster_distance_min for px, py in cluster_centers)):
                continue
            # Place cells_per_cluster unique cells in this cluster
            placed_in_cluster = 0
            cell_attempts = 0
            while (
                placed_in_cluster < cells_per_cluster and 
                cell_attempts < cells_per_cluster * 10 and 
                len(seeded_cells) < target_food_cells
            ):
                cell_attempts += 1
                fx = int(np.clip(np.random.normal(cx, cluster_spread), 0, width - 1))
                fy = int(np.clip(np.random.normal(cy, cluster_spread), 0, height - 1))
                if abs(fx - nest_cx) < food_distance_min and abs(fy - nest_cy) < food_distance_min:
                    continue
                if (fx, fy) in seeded_cells:
                    continue
                ca = self._get_cell_agent(self.grid[fx, fy])
                if ca and not ca.is_nest:
                    ca.food += self.random.uniform(3.0, 8.0)
                    seeded_cells.add((fx, fy))
                    placed_in_cluster += 1
            if placed_in_cluster > 0:
                cluster_centers.append((cx, cy))
                clusters_placed += 1
        
        print(f"Actual clusters placed: {len(cluster_centers)}")
        food_cells = sum(1 for cell in self.grid for ca in cell.agents if isinstance(ca, cell_agent) and ca.food > 0)
        total_cells = self.grid.width * self.grid.height
        print(f"Food coverage: {food_cells / total_cells * 100:.2f}% ({food_cells} of {total_cells} cells)")
        
        # Create creatures at nest
        nest_cell = self.grid[self.nest_location]
        for i in range(creature_num):
            creature = CreatureAgent(self, len(self.agents), nest_cell)
            self.agents.add(creature)

    def _get_cell_agent(self, cell) -> cell_agent | None:
        for obj in cell.agents:
            if isinstance(obj, cell_agent):
                return obj
        return None

    def get_average_energy(self):
        agents = [a for a in self.agents_by_type[CreatureAgent] if a.alive]
        if not agents:
            return 0
        return sum(a.energy for a in agents) / len(agents)
    
    def update_death_count(self):
        # Used for death stats
        self.dead_creatures += 1

    def export_data_to_csv(self, filename = None):
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"{timestamp}.csv"
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(filepath)

    def step(self):
        # Used to force stop
        if not self.running:
            return
        # Stop when there are no creatures alive
        if not any(a.alive for a in self.agents_by_type[CreatureAgent]):
            self.datacollector.collect(self)
            self.running = False
            self.export_data_to_csv()
            return
        self.agents_by_type[cell_agent].do("step")
        # Randomize order of activation to prevent bias
        self.agents_by_type[CreatureAgent].shuffle().do("step")
        self.datacollector.collect(self)
