from controller import Robot
import math
import random

DISTANCE_SENSORS_NUMBER = 8
LIGHT_SENSORS_NUMBER = 8
MAX_SPEED = 4.0

OBSTACLE_THRESHOLD = 180.0
WALL_THRESHOLD = 250.0
GAP_THRESHOLD = 140.0
LIGHT_THRESHOLD_RATIO = 0.12
LIGHT_GAP_THRESHOLD = 0.12
LIGHT_STEER_GAIN = 0.05

COMM_CHANNEL = 7

EXPLORE = "EXPLORE"
WALL_FOLLOW = "WALL_FOLLOW"
RECRUIT = "RECRUIT"
ATTRACTED = "ATTRACTED"
CROSSING = "CROSSING"
PHOTOTAXIS = "PHOTOTAXIS"

robot = Robot()
name = robot.getName()
timestep = int(robot.getBasicTimeStep())

# Initialize proximity sensors
distance_sensors = []
for i in range(DISTANCE_SENSORS_NUMBER):
    sensor = robot.getDevice("ps" + str(i))
    sensor.enable(timestep)
    distance_sensors.append(sensor)

# Initialize light sensors
light_sensors = []
for i in range(LIGHT_SENSORS_NUMBER):
    sensor = robot.getDevice("ls" + str(i))
    sensor.enable(timestep)
    light_sensors.append(sensor)

# Configure the wheel motors
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Configure communication
emitter = robot.getDevice("emitter")
receiver = robot.getDevice("receiver")
emitter.setChannel(COMM_CHANNEL)
receiver.setChannel(COMM_CHANNEL)
receiver.enable(timestep)

# Choose a stable wall-following side
try:
    robot_id = int(name.split()[-1])
except ValueError:
    robot_id = 0
wall_side = 1 if robot_id % 2 == 0 else -1

state = EXPLORE
stuck_steps = 0
crossing_steps = 0
STUCK_STEP_LIMIT = int(3000 / timestep)

# Main control loop: read sensors, process messages and update behavior
while robot.step(timestep) != -1:
    ps_values = [sensor.getValue() for sensor in distance_sensors]
    ls_values = [sensor.getValue() for sensor in light_sensors]

    # Interpret light sensor readings
    left_light = sum(ls_values[4:8]) / 4.0
    right_light = sum(ls_values[0:4]) / 4.0
    front_light = (ls_values[0] + ls_values[7]) / 2.0

    front = ps_values[0] + ps_values[7]
    left_side = ps_values[5] + ps_values[6]
    right_side = ps_values[1] + ps_values[2]
    front_blocked = front > WALL_THRESHOLD

    best_strength = 0.0
    best_direction = None

    # Read any incoming recruitment messages from nearby robots
    while receiver.getQueueLength() > 0:
        message = receiver.getString()
        if message.startswith("HOLE"):
            strength = receiver.getSignalStrength()
            if strength > best_strength:
                best_strength = strength
                best_direction = receiver.getEmitterDirection()
        receiver.nextPacket()

    left_speed = 0.5 * MAX_SPEED
    right_speed = 0.5 * MAX_SPEED

    # Wander until the robot sees a wall, a hole or a recruitment message
    if state == EXPLORE:
        if front_blocked:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> WALL_FOLLOW: Front wall detected")
            stuck_steps = 0
            state = WALL_FOLLOW
        elif best_direction is not None:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> ATTRACTED: Received signal from hole")
            state = ATTRACTED
        else:
            if front > OBSTACLE_THRESHOLD:
                left_speed = -0.3 * MAX_SPEED
                right_speed = 0.1 * MAX_SPEED
            elif left_side > OBSTACLE_THRESHOLD:
                left_speed = 0.5 * MAX_SPEED
                right_speed = 0.1 * MAX_SPEED
            elif right_side > OBSTACLE_THRESHOLD:
                left_speed = 0.1 * MAX_SPEED
                right_speed = 0.5 * MAX_SPEED
            else:
                left_speed = 0.5 * MAX_SPEED + random.uniform(-0.15, 0.15) * MAX_SPEED
                right_speed = 0.5 * MAX_SPEED + random.uniform(-0.15, 0.15) * MAX_SPEED

    # Stay close to the wall and look for a passage
    elif state == WALL_FOLLOW:
        side_reading = left_side if wall_side > 0 else right_side
        other_side_reading = right_side if wall_side > 0 else left_side

        if front_blocked:
            left_speed = -0.25 * MAX_SPEED - 0.2 * MAX_SPEED * wall_side
            right_speed = -0.25 * MAX_SPEED + 0.2 * MAX_SPEED * wall_side
            stuck_steps += 1
            if stuck_steps > STUCK_STEP_LIMIT:
                print(f"[{robot.getTime():.3f}s] {name}: {state} -> EXPLORE: Stuck too long")
                stuck_steps = 0
                state = EXPLORE

        elif side_reading < GAP_THRESHOLD or other_side_reading < GAP_THRESHOLD * 0.8:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> RECRUIT: Hole detected")
            stuck_steps = 0
            state = RECRUIT

        elif max(left_light, right_light) > LIGHT_GAP_THRESHOLD:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> RECRUIT: Light detected")
            stuck_steps = 0
            state = RECRUIT

        else:
            stuck_steps = 0
            base = 0.3 * MAX_SPEED
            correction = 0.12 * MAX_SPEED

            # Slight steering toward the brighter side
            if right_light > left_light + 0.03:
                correction += LIGHT_STEER_GAIN * MAX_SPEED
            elif left_light > right_light + 0.03:
                correction -= LIGHT_STEER_GAIN * MAX_SPEED

            left_speed = base - correction * wall_side
            right_speed = base + correction * wall_side

    # Announce that a hole has been found
    elif state == RECRUIT:
        emitter.send(f"HOLE:{name}".encode("utf-8"))
        print(f"[{robot.getTime():.3f}s] {name}: {state} -> CROSSING")
        crossing_steps = 0
        state = CROSSING

    # Move toward the source of the recruitment message
    elif state == ATTRACTED:
        if best_direction is not None:
            dx, dz = best_direction[0], best_direction[2]
            angle = math.atan2(dx, dz)
            turn = max(-1.0, min(1.0, angle))
            left_speed = 0.5 * MAX_SPEED * (1.0 - turn)
            right_speed = 0.5 * MAX_SPEED * (1.0 + turn)
        else:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> EXPLORE: Lost recruitment direction")
            state = EXPLORE

        if front_blocked:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> WALL_FOLLOW: Front wall detected")
            state = WALL_FOLLOW

    # Drive through the opening and look for the light beyond it
    elif state == CROSSING:
        crossing_steps += 1

        if left_light > right_light + 0.03:
            left_speed = 0.45 * MAX_SPEED
            right_speed = 0.7 * MAX_SPEED
        elif right_light > left_light + 0.03:
            left_speed = 0.7 * MAX_SPEED
            right_speed = 0.45 * MAX_SPEED
        elif front > OBSTACLE_THRESHOLD:
            left_speed = -0.2 * MAX_SPEED
            right_speed = 0.1 * MAX_SPEED
        else:
            left_speed = 0.6 * MAX_SPEED
            right_speed = 0.6 * MAX_SPEED

        if max(left_light, right_light) > LIGHT_GAP_THRESHOLD or crossing_steps > 80:
            print(f"[{robot.getTime():.3f}s] {name}: {state} -> PHOTOTAXIS: Light detected or crossing timeout")
            state = PHOTOTAXIS

    # Steer toward the light source
    elif state == PHOTOTAXIS:
        reference_light_value = (ls_values[0] + ls_values[7]) / 2.0
        right_light_value = sum(ls_values[0:4]) / 4.0
        left_light_value = sum(ls_values[4:8]) / 4.0
        threshold = LIGHT_THRESHOLD_RATIO * reference_light_value

        if reference_light_value - left_light_value > threshold:
            left_speed = -0.25 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED
        elif reference_light_value - right_light_value > threshold:
            left_speed = 0.5 * MAX_SPEED
            right_speed = -0.25 * MAX_SPEED
        else:
            left_speed = 0.5 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED

    # Clamp the wheel speeds and apply them to the motors
    left_speed = max(-MAX_SPEED, min(MAX_SPEED, left_speed))
    right_speed = max(-MAX_SPEED, min(MAX_SPEED, right_speed))
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)