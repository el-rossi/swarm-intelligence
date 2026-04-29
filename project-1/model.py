import numpy as np
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.datacollection import DataCollector
from agent import CreatureAgent, RESTING, FORAGING, RETURNING_LOADED, RETURNING_EMPTY
from cell_agent import cell_agent

class SwarmModel(Model):

    def __init__(self,
        # Environment
        width: int                  = 60,
        height: int                 = 60,
        creature_num: int           = 50,
        cluster_num: int            = 12,
        cluster_spread: float       = 1.5,
        food_distance_min: int      = 6,
        food_coverage: float        = 0.15,
        # Energy
        energy_max: float           = 200.0,
        energy_drain_base: float    = 0.3,
        energy_drain_move: float    = 0.2,
        energy_forage_min: float    = 40.0,
        # Temperature
        temperature_safe: float     = 20.0,
        temperature_critical: float = 100.0,
        cool_rate: float            = 1.5,
        heat_rate: float            = 0.8,
        heat_abort_ratio: float     = 0.75,
        # Movement
        speed_max: int              = 3,
        momentum_weight: float      = 2.0,
        outward_weight: float       = 0.1,
        # ACO
        pheromone_deposit: float    = 10.0,
        evaporation_rate: float     = 0.05,
        exploration_weight: float   = 1.0
    ):
        super().__init__()
        # Environment
        self.cluster_spread         = cluster_spread
        self.food_distance_min      = food_distance_min
        self.food_coverage          = food_coverage
        # Energy
        self.energy_max             = energy_max
        self.energy_drain_base      = energy_drain_base
        self.energy_drain_move      = energy_drain_move
        self.energy_forage_min      = energy_forage_min
        # Temperature
        self.temperature_safe       = temperature_safe
        self.temperature_critical   = temperature_critical
        self.cool_rate              = cool_rate
        self.heat_rate              = heat_rate
        self.heat_abort_ratio       = heat_abort_ratio
        # Movement
        self.speed_max              = speed_max
        self.momentum_weight        = momentum_weight
        self.outward_weight         = outward_weight
        # ACO
        self.pheromone_deposit      = pheromone_deposit
        self.evaporation_rate       = evaporation_rate
        self.exploration_weight     = exploration_weight
        # Grid
        self.grid = OrthogonalMooreGrid([width, height], torus=False, capacity=creature_num+1)
        self.nest_location = (width // 2, height // 2)
        # Stats
        self.food_collected: float = 0.0
        self.dead_creatures: int = 0
        self.datacollector = DataCollector(
            model_reporters={
                "Food Collected":   lambda m: m.food_collected,
                "Total Energy":     lambda m: sum(a.energy for a in m.agents_by_type[CreatureAgent] if a.alive),
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
        target_food_cells = int(width * height * self.food_coverage)
        cells_per_cluster = max(1, target_food_cells // cluster_num)
        nest_cx, nest_cy  = self.nest_location
        seeded  = 0
        attempts = 0
        while seeded < cluster_num and attempts < 2000:
            attempts += 1
            # Set cluster center
            cx = self.random.randint(0, width - 1)
            cy = self.random.randint(0, height - 1)
            if abs(cx - nest_cx) < self.food_distance_min and abs(cy - nest_cy) < self.food_distance_min:
                continue
            for _ in range(cells_per_cluster):
                # Set food cell around cluster center with normal distribution
                fx = int(np.clip(np.random.normal(cx, self.cluster_spread), 0, width - 1))
                fy = int(np.clip(np.random.normal(cy, self.cluster_spread), 0, height - 1))
                if abs(fx - nest_cx) < self.food_distance_min and abs(fy - nest_cy) < self.food_distance_min:
                    continue
                ca = self._get_cell_agent(self.grid[fx, fy])
                if ca and not ca.is_nest:
                    ca.food += self.random.uniform(3.0, 8.0)
            seeded += 1
        
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
    
    def update_death_count(self):
        # Used for death stats
        self.dead_creatures += 1

    def step(self):
        # Used to force stop
        if not self.running:
            return
        # Stop when there are no creatures alive
        if not any(a.alive for a in self.agents_by_type[CreatureAgent]):
            self.datacollector.collect(self)
            self.running = False
            return
        self.agents_by_type[cell_agent].do("step")
        # Randomize order of activation to prevent bias
        self.agents_by_type[CreatureAgent].shuffle().do("step")
        self.datacollector.collect(self)
