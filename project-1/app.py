import numpy as np
from mesa.visualization import (Slider, SolaraViz, SpaceRenderer, make_plot_component)
from mesa.visualization.components import AgentPortrayalStyle
from model import SwarmModel
from agent import CreatureAgent, RESTING, FORAGING, RETURNING_LOADED, RETURNING_EMPTY
from cell_agent import cell_agent

STATE_COLORS = {
    RESTING:          "lightskyblue",
    FORAGING:         "darkslateblue",
    RETURNING_EMPTY:  "mediumpurple",
    RETURNING_LOADED: "gold"
}

def agent_portrayal(agent):
    if agent is None:
        return
    if isinstance(agent, CreatureAgent):
        return AgentPortrayalStyle(
            marker = "o",
            size = 20,
            zorder = 2,
            color = STATE_COLORS.get(agent.state, "grey")
        )
    if isinstance(agent, cell_agent):
        marker = "s"
        if agent.is_nest:
            color = "saddlebrown"
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
            marker = marker,
            size = 30,
            zorder = 0,
            color = color
        )

MODEL_PARAMS_DEFAULTS = [
    60,     # width
    60,     # height
    50,     # creature_num
    12,     # cluster_num
    1.5,    # cluster_spread
    0.15,   # food_coverage
    100.0,  # temperature_critical
    0.8,    # heat_rate
    3,      # speed_max
    10.0,   # pheromone_deposit
    0.05,   # evaporation_rate
    1.0     # exploration_weight
]
model_params = {
    "width": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[0],
        "label":    "Grid width",
        "min":      20,
        "max":      100,
        "step":     5
    },
    "height": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[1],
        "label":    "Grid height",
        "min":      20,
        "max":      100,
        "step":     5
    },
    "creature_num": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[2],
        "label":    "Creature number",
        "min":      10,
        "max":      80,
        "step":     5
    },
    "cluster_num": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[3],
        "label":    "Cluster number",
        "min":      1,
        "max":      15,
        "step":     1
    },
    "cluster_spread": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[4],
        "label":    "Cluster spread",
        "min":      0.5,
        "max":      3.5,
        "step":     0.5
    },
    "food_coverage": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[5],
        "label":    "Food coverage",
        "min":      0.05,
        "max":      0.20,
        "step":     0.05
    },
    "temperature_critical": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[6],
        "label":    "Critical temperature",
        "min":      20.0,
        "max":      200.0,
        "step":     10.0
    },
    "heat_rate": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[7],
        "label":    "Heat rate",
        "min":      0.1,
        "max":      3.0,
        "step":     0.1
    },
    "speed_max": {
        "type":     "SliderInt",
        "value":    MODEL_PARAMS_DEFAULTS[8],
        "label":    "Speed",
        "min":      1,
        "max":      5,
        "step":     1
    },
    "pheromone_deposit": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[9],
        "label":    "Pheromone deposit",
        "min":      1.0,
        "max":      50.0,
        "step":     1.0
    },
    "evaporation_rate": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[10],
        "label":    "Pheromone evaporation",
        "min":      0.01,
        "max":      0.30,
        "step":     0.01
    },
    "exploration_weight": {
        "type":     "SliderFloat",
        "value":    MODEL_PARAMS_DEFAULTS[11],
        "label":    "Exploration weight",
        "min":      0.0,
        "max":      5.0,
        "step":     0.25
    }
}
model = SwarmModel(
    width                   = MODEL_PARAMS_DEFAULTS[0],
    height                  = MODEL_PARAMS_DEFAULTS[1],
    creature_num            = MODEL_PARAMS_DEFAULTS[2],
    cluster_num             = MODEL_PARAMS_DEFAULTS[3],
    cluster_spread          = MODEL_PARAMS_DEFAULTS[4],
    food_coverage           = MODEL_PARAMS_DEFAULTS[5],
    temperature_critical    = MODEL_PARAMS_DEFAULTS[6],
    heat_rate               = MODEL_PARAMS_DEFAULTS[7],
    speed_max               = MODEL_PARAMS_DEFAULTS[8],
    pheromone_deposit       = MODEL_PARAMS_DEFAULTS[9],
    evaporation_rate        = MODEL_PARAMS_DEFAULTS[10],
    exploration_weight      = MODEL_PARAMS_DEFAULTS[11]
)

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    width = renderer.space.width
    height = renderer.space.height
    ax.set_xticks(np.arange(-0.5, width,  1), minor = True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor = True)
    ax.grid(which = "minor", color = "grey", linestyle = "-", linewidth = 0.5)

renderer = SpaceRenderer(model, backend = "matplotlib").setup_agents(agent_portrayal)
renderer.post_process = post_process_space
renderer.draw_agents()
renderer.render()

CollectedFoodPlot   = make_plot_component({"Food Collected": "gold"}) # TODO add pheromone deposited
AliveDeadPlot       = make_plot_component({"Alive Creatures": "green", "Dead Creatures": "red"})
EnergyPlot          = make_plot_component({"Total Energy": "royalblue"})
StatePlot           = make_plot_component({
    "Resting":          "lightskyblue",
    "Foraging":         "darkslateblue",
    "Returning Loaded": "gold",
    "Returning Empty":  "mediumpurple"
})

# TODO fix overlap between grid and state plot
page = SolaraViz(
    model,
    renderer,
    components = [EnergyPlot, StatePlot, CollectedFoodPlot, AliveDeadPlot],
    model_params = model_params,
    name = "ACO Swarm - Survival Simulation"
)
page
