import numpy as np
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from agent import CreatureAgent
from cell_agent import cell_agent

class SwarmModel(Model):

    def __init__(
        self,
        # Environment
        width: int                  = 60,
        height: int                 = 60,
        num_creatures: int          = 50,
        num_food_clusters: int      = 12,
        cluster_spread: float       = 1.5,
        # Creatures
        energy_max: float           = 200.0,
        temperature_safe: float     = 20.0,
        temperature_critical: float = 100.0,
        heat_rate: float            = 0.8,
        cool_rate: float            = 1.5,
        base_energy_drain: float    = 0.3,
        move_energy_cost: float     = 0.2,
        # rest_energy_recovery: float  = 1.0,   # enable for energy regeneration
        min_energy_to_forage: float = 40.0,
        abort_heat_ratio: float     = 0.75,
        max_speed: int              = 3,
        # ACO
        pheromone_deposit: float    = 10.0,
        evaporation_rate: float     = 0.05,
        exploration_weight: float   = 1.0,
        momentum_weight: float      = 2.0,
        outward_weight: float       = 0.1
    ):
        super().__init__()
        self.energy_max            = energy_max
        self.temperature_safe      = temperature_safe
        self.temperature_critical  = temperature_critical
        self.heat_rate             = heat_rate
        self.cool_rate             = cool_rate
        self.base_energy_drain     = base_energy_drain
        self.move_energy_cost      = move_energy_cost
        # self.rest_energy_recovery  = rest_energy_recovery     # enable for energy regeneration
        self.min_energy_to_forage  = min_energy_to_forage
        self.abort_heat_ratio      = abort_heat_ratio
        self.max_speed             = max_speed
        self.pheromone_deposit     = pheromone_deposit
        self.evaporation_rate      = evaporation_rate
        self.exploration_weight    = exploration_weight
        self.momentum_weight       = momentum_weight
        self.outward_weight        = outward_weight
        self.cluster_spread        = cluster_spread

        self.grid = OrthogonalMooreGrid([width, height], torus=False, capacity=num_creatures+1)
        self.nest_location = (width // 2, height // 2)

        for cell in self.grid:
            ca = cell_agent(self, len(self.agents), cell)
            self.agents.add(ca)

        nest_ca = self._get_cell_agent(self.grid[self.nest_location])
        if nest_ca:
            nest_ca.is_nest = True

        target_food_cells = int(width * height * 0.15)
        cells_per_cluster = max(1, target_food_cells // num_food_clusters)
        nest_cx, nest_cy  = self.nest_location
        seeded  = 0
        attempts = 0
        while seeded < num_food_clusters and attempts < 2000:
            attempts += 1
            cx = self.random.randint(0, width - 1)
            cy = self.random.randint(0, height - 1)
            # Keep clusters away from the nest      # TODO param?
            if abs(cx - nest_cx) < 6 and abs(cy - nest_cy) < 6:
                continue
            for _ in range(cells_per_cluster):
                fx = int(np.clip(np.random.normal(cx, self.cluster_spread), 0, width - 1))
                fy = int(np.clip(np.random.normal(cy, self.cluster_spread), 0, height - 1))
                ca = self._get_cell_agent(self.grid[fx, fy])
                if ca and not ca.is_nest:
                    ca.food += self.random.uniform(3.0, 8.0)
            seeded += 1

        nest_cell = self.grid[self.nest_location]
        for i in range(num_creatures):
            creature = CreatureAgent(self, len(self.agents), nest_cell)
            self.agents.add(creature)

    def _get_cell_agent(self, cell) -> cell_agent | None:
        for obj in cell.agents:
            if isinstance(obj, cell_agent):
                return obj
        return None

    def step(self):
        self.agents_by_type[cell_agent].do("step")
        self.agents_by_type[CreatureAgent].shuffle().do("step")
        alive_agents = self.agents_by_type[CreatureAgent]
        if len(alive_agents) == 0 or not any(a.alive for a in alive_agents):
            self.running = False