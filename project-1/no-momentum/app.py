import numpy as np
from mesa.visualization import (Slider, SolaraViz, SpaceRenderer, make_plot_component)
from mesa.visualization.components import AgentPortrayalStyle
from model import SwarmModel
from agent import CreatureAgent, RESTING, FORAGING, RETURNING_LOADED, RETURNING_EMPTY
from cell_agent import cell_agent

STATE_COLORS = {
    RESTING:          "lightskyblue",
    FORAGING:         "darkslateblue",
    RETURNING_EMPTY:  "slateblue",
    RETURNING_LOADED: "gold"
}

def agent_portrayal(agent):
    if agent is None:
        return
    if isinstance(agent, CreatureAgent):
        return AgentPortrayalStyle(
            marker="o",
            size=20,
            zorder=2,
            color=STATE_COLORS.get(agent.state, "grey"),
        )
    if isinstance(agent, cell_agent):
        marker = "s"
        if agent.is_nest:
            color = "deepskyblue"
            marker = "D"
        elif agent.food > 0:
            intensity = min(1.0, agent.food / 8.0)
            g = int(55 + 150 * intensity)
            color = f"#00{g:02x}00"
            marker = "D"
        elif agent.pheromone > 0:
            intensity = min(1.0, agent.pheromone / 50.0)
            r = 255
            g = int(255 * (1.0 - intensity))
            b = int(224 * (1.0 - intensity) + 80 * intensity)
            color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            color = "beige"
        return AgentPortrayalStyle(
            marker=marker,
            size=30,
            zorder=0,
            color=color
        )

MODEL_PARAMS_DEFAULTS = [60, 60, 50, 12]
model_params = {
    "width": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[0],
        "label":    "Grid Width",
        "min":      20,
        "max":      100,
        "step":     5
    },
    "height": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[1],
        "label":    "Grid Height",
        "min":      20,
        "max":      100,
        "step":     5
    },
    "num_creatures": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[2],
        "label":    "Number of Creatures",
        "min":      10,
        "max":      80,
        "step":     5
    },
    "num_food_clusters": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[3],
        "label":    "Food Clusters",
        "min":      1,
        "max":      15,
        "step":     1
    },
    "cluster_spread": {
        "type":     "SliderFloat",
        "value":    1.5,
        "label":    "Cluster Spread",
        "min":      0.5,
        "max":      5.0,
        "step":     0.5
    },
    "evaporation_rate": {
        "type":     "SliderFloat",
        "value":    0.05,
        "label":    "Pheromone Evaporation Rate",
        "min":      0.01,
        "max":      0.30,
        "step":     0.01
    },
    "heat_rate": {
        "type":     "SliderFloat",
        "value":    0.8,
        "label":    "Heat Rate (outside nest)",
        "min":      0.1,
        "max":      3.0,
        "step":     0.1
    },
    "temperature_critical": {
        "type":     "SliderFloat",
        "value":    100.0,
        "label":    "Critical Temperature (Tcrit)",
        "min":      20.0,
        "max":      200.0,
        "step":     10.0
    },
    "energy_max": {
        "type":     "SliderFloat",
        "value":    200.0,
        "label":    "Max Energy (Emax)",
        "min":      50.0,
        "max":      500.0,
        "step":     25.0
    },
    "max_speed": {
        "type":     "SliderInt",
        "value":    3,
        "label":    "Max Speed (cells/tick)",
        "min":      1,
        "max":      5,
        "step":     1
    },
    "pheromone_deposit": {
        "type":     "SliderFloat",
        "value":    10.0,
        "label":    "Pheromone Deposit Amount",
        "min":      1.0,
        "max":      50.0,
        "step":     1.0
    },
    "exploration_weight": {
        "type":     "SliderFloat",
        "value":    1.0,
        "label":    "Exploration Weight",
        "min":      0.0,
        "max":      5.0,
        "step":     0.25
    }
}
model = SwarmModel(*MODEL_PARAMS_DEFAULTS)

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    width  = renderer.space.width
    height = renderer.space.height
    ax.set_xticks(np.arange(-0.5, width,  1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.grid(which="minor", color="grey", linestyle="-", linewidth=0.5)

renderer = SpaceRenderer(
    model,
    backend="matplotlib",
).setup_agents(agent_portrayal)
renderer.post_process = post_process_space
renderer.draw_agents()
renderer.render()

page = SolaraViz(
    model,
    renderer,
    components=[],
    model_params=model_params,
    name="ACO Swarm - Survival Simulation",
)
page
