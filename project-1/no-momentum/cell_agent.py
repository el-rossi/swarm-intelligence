from mesa.discrete_space import FixedAgent

class cell_agent(FixedAgent):

    def __init__(self, model, unique_id, cell):
        super().__init__(model)
        self.unique_id = unique_id
        self.cell = cell
        self.is_nest: bool = False
        self.food: float = 0.0 
        self.pheromone: float = 0.0

    def step(self):
        self.pheromone = max(0.0, self.pheromone * (1.0 - self.model.evaporation_rate))