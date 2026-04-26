import numpy as np
from mesa.discrete_space import CellAgent
from cell_agent import cell_agent

RESTING          = "resting"
FORAGING         = "foraging"
RETURNING_LOADED = "returning_loaded"
RETURNING_EMPTY  = "returning_empty"

class CreatureAgent(CellAgent):

    def __init__(self, model, unique_id, cell):
        super().__init__(model)
        self.unique_id                  = unique_id
        self.cell                       = cell
        self.state: str                 = RESTING
        self.alive: bool                = True
        self.energy: float              = model.energy_max 
        self.temperature: float         = model.temperature_safe
        self.estimated_richness: float  = 0.0

    def _get_cell_agent(self, cell) -> cell_agent | None:
        for obj in cell.agents:
            if isinstance(obj, cell_agent):
                return obj
        return None

    def _is_at_nest(self) -> bool:
        ca = self._get_cell_agent(self.cell)
        return ca is not None and ca.is_nest

    def _sense_food_nearby(self) -> cell_agent | None:
        local = self.cell.get_neighborhood(radius=1, include_center=True)
        for c in local:
            ca = self._get_cell_agent(c)
            if ca and ca.food > 0:
                return ca
        return None

    def _move_toward_nest(self, deposit_pheromone: bool = False):
        nx, ny = self.model.nest_location
        deposit = self.model.pheromone_deposit * (1.0 + self.estimated_richness)
        for _ in range(self.model.max_speed):
            if deposit_pheromone:
                ca = self._get_cell_agent(self.cell)
                if ca:
                    ca.pheromone += deposit
            neighbors = list(self.cell.get_neighborhood(radius=1, include_center=False))
            best_cell = min(
                neighbors,
                key=lambda c: abs(c.coordinate[0] - nx) + abs(c.coordinate[1] - ny),
                default=None
            )
            if best_cell is None:
                break
            self.cell = best_cell
            if self._is_at_nest():
                break

    def _move_foraging(self):
        for _ in range(self.model.max_speed):
            neighbors = list(self.cell.get_neighborhood(radius=1, include_center=False))
            if not neighbors:
                break
            weights = []
            for c in neighbors:
                ca = self._get_cell_agent(c)
                pheromone = ca.pheromone if ca else 0.0
                weights.append(pheromone + self.model.exploration_weight)
            total = sum(weights)
            probs = [w / total for w in weights]
            self.cell = self.model.random.choices(neighbors, weights=probs, k=1)[0]

    def _check_death(self) -> bool:
        if self.energy <= 0 or self.temperature >= self.model.temperature_critical:
            self.alive = False
            self.remove()
            return True
        return False

    def _step_resting(self):
        self.temperature = max(
            self.model.temperature_safe,
            self.temperature - self.model.cool_rate,
        )
        # Recover energy while resting
        # self.energy = min(
        #     self.model.energy_max,
        #     self.energy + self.model.rest_energy_recovery,
        # )
        if (
            self.temperature <= self.model.temperature_safe
            and self.energy >= self.model.min_energy_to_forage
        ):
            self.state = FORAGING

    def _step_foraging(self):
        self.temperature += self.model.heat_rate
        self.energy -= self.model.base_energy_drain + self.model.move_energy_cost
        if self._check_death():
            return
        food_ca = self._sense_food_nearby()
        if food_ca is not None:
            food_ca.food = max(0.0, food_ca.food - 1.0)
            self.estimated_richness = food_ca.food
            self.state = RETURNING_LOADED
            return
        if (
            self.temperature >= self.model.temperature_critical * self.model.abort_heat_ratio
            or self.energy <= self.model.min_energy_to_forage
        ):
            self.state = RETURNING_EMPTY
            return
        self._move_foraging()

    def _step_returning(self):
        self.temperature += self.model.heat_rate
        self.energy -= self.model.base_energy_drain + self.model.move_energy_cost
        if self._check_death():
            return
        if self._is_at_nest():
            self.state = RESTING
        else:
            self._move_toward_nest(deposit_pheromone=(self.state == RETURNING_LOADED))

    def step(self):
        if not self.alive:
            return
        if self.state == RESTING:
            self._step_resting()
        elif self.state == FORAGING:
            self._step_foraging()
        elif self.state in (RETURNING_LOADED, RETURNING_EMPTY):
            self._step_returning()
