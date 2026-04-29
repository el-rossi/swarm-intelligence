# Project 1: Swarm Intelligence Simulation

This project implements a grid-based agent-based simulation of swarm intelligence, inspired by ant foraging behavior. The simulation is built using the [Mesa](https://mesa.readthedocs.io/) framework and visualized interactively with [Solara](https://solara.dev/).

## Features

- **Grid World:** Agents (creatures) move on a 2D grid containing food clusters, pheromones, and a central nest.
- **Agent States:** Each agent can be resting, foraging, returning loaded, or returning empty.
- **Pheromone Communication:** Agents deposit pheromones to guide others toward food sources.
- **Energy and Temperature:** Agents consume energy and accumulate heat as they move and forage. They must rest to cool down and recover.
- **Food Collection:** Agents search for food, collect it, and return it to the nest.
- **Parameter Controls:** The simulation exposes sliders for key parameters (e.g., number of agents, food clusters, energy, temperature, pheromone settings) for interactive experimentation.
- **Live Plots:** The UI displays real-time plots of total energy, agent states, food collected, and alive/dead agents. This feature was excluded from the project submission because of layout issues (the charts overlapped with the grid) and were used only to collect data to evaluate the performance of the model (see [Experiments](#experiments)).

## How it works

- Agents start at the nest and alternate between resting, foraging, and returning states.
- Food is distributed in clusters, with a minimum distance from the nest.
- Agents use a combination of pheromone following, momentum, and exploration to find food.
- Energy and temperature constraints force agents to rest and can lead to death if not managed.
- The simulation ends when all agents are dead.


## Experiments

1. **Number of Creatures**
   - Change `creature_num` (default: 50)
   - Observe: Food collected, survival rate, time to extinction, congestion effects

2. **Number of Food Clusters**
   - Change `cluster_num` (default: 12)
   - Observe: Foraging efficiency, time to food depletion, agent distribution

3. **Cluster Spread**
   - Change `cluster_spread` 
   - Observe: How food spatial distribution affects foraging and survival

4. **Food Distance from Nest**
   - Change `food_distance_min` 
   - Observe: Impact on energy spent, survival, and food collection

5. **Energy Parameters**
   - Change `energy_max`, `energy_drain_base`, `energy_drain_move`, `min_energy_to_forage`
   - Observe: How energy constraints affect agent lifespan and foraging

6. **Temperature Parameters**
   - Change `temperature_critical`, `heat_rate`, `cool_rate`
   - Observe: Impact on agent mortality and foraging cycles

7. **Pheromone Parameters**
   - Change `pheromone_deposit`, `evaporation_rate`
   - Observe: How communication affects foraging efficiency and path formation

8. **Exploration and Movement Biases**
   - Change `exploration_weight`, `momentum_weight`, `outward_weight`
   - Observe: How agent movement strategies affect resource discovery and exploitation

9. **Grid Size**
   - Change `width` and `height` (default: 60x60)
   - Observe: Effects on agent density, foraging, and survival