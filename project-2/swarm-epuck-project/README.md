# Swarm E-Puck Project

## Overview
The Swarm E-Puck Project is designed to simulate a swarm of e-puck robots navigating through a wall with unknown passages in a 2 m × 3 m arena. The project utilizes Webots for simulation and includes a custom controller that enables the robots to exhibit swarm behavior, local sensing, and decision-making processes.

## Project Structure
- **worlds/epuck_swarm.wbt**: This file defines the simulation environment for the e-puck robots. It includes the arena layout, wall with holes, light source, and the initial positions of the robots.
  
- **controllers/epuck_swarm_controller/epuck_swarm_controller.py**: This file contains the controller logic for the e-puck robots. It implements the swarm behavior, local sensing, and decision-making processes required for the robots to navigate through the wall. The controller uses the robot's sensors to detect holes and communicate with nearby robots.

- **protos/CustomEpuck.proto**: This file defines a custom prototype for the e-puck robots, allowing for specific configurations and behaviors tailored to the swarm's needs. It may include parameters for robot size, sensor range, and communication capabilities.

## Instructions
1. Ensure you have Webots installed on your machine.
2. Clone or download the project repository.
3. Open the project in Webots.
4. Load the `epuck_swarm.wbt` world file.
5. Start the simulation to observe the swarm behavior of the e-puck robots navigating through the wall.

## Objectives
- To demonstrate swarm robotics principles using e-puck robots.
- To implement local sensing and communication among robots.
- To navigate through an environment with unknown passages effectively.

## Acknowledgments
This project is inspired by swarm intelligence and robotics research, aiming to explore collaborative behaviors in robotic systems.