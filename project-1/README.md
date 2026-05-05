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

## Analysis

The simulation data was used to analyze the collective behavior and performance of the swarms. These visualizations provide insights into agent dynamics, resource utilization, and spatial patterns over time.

### Plots

**States**  
A stacked plot showing the number of agents in each state at every simulation step. It reveals how the swarm’s activity evolves, highlighting periods of foraging, rest and mortality.

**Energy**  
A line plot of the average energy of all living agents at each step. It indicates the overall health of the swarm.

**Food**  
A line plot tracking the cumulative amount of food collected by all agents over time. It measures the swarm’s foraging efficiency.

**Pheromone**  
A line plot showing the total amount of pheromone present in the environment at each step. It visualizes the dynamics of pheromone deposition and evaporation, which are key to collective pathfinding and communication.

### Heatmaps

**Food**  
A spatial heatmap showing the total amount of food collected from each cell over the course of the simulation. It identifies the spatial reach of the swarm’s foraging activity.

**Pheromone**  
A spatial heatmap representing the sum of all pheromone deposited in each cell throughout the simulation. It highlights frequently used paths and collective trail formation, revealing the swarm’s preferred routes between nest and food sources.

## Experiments

| # | Experiment                        | Affected Parameters                                                                 | Evaluation Metrics                                      |
|---|-----------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Number of Creatures               | `creature_num`                                                                      | Food collected, survival rate, time to extinction       |
| 2 | Number of Food Clusters           | `cluster_num`                                                                       | Foraging efficiency, time to food depletion, agent distribution |
| 3 | Cluster Spread                    | `cluster_spread`                                                                    | Food spatial distribution effect on foraging and survival |
| 4 | Temperature Parameters            | `temperature_critical`, `heat_rate`, ~~`cool_rate`~~                                | Agent mortality, foraging cycles                        |
| 5 | Pheromone Parameters              | `pheromone_deposit`, `evaporation_rate`                                             | Foraging efficiency, path formation                     |
| 6 | Exploration and Movement Biases   | `exploration_weight`, ~~`momentum_weight`~~, ~~`outward_weight`~~                   | Resource discovery and exploitation                     |
| 7 | Grid Size                         | `width`, `height`                                                                   | Agent density, foraging, survival                       |

