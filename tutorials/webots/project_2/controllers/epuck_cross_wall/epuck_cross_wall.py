from controller import Robot, Motor, DistanceSensor, Emitter, Receiver
import math
import random
 
DISTANCE_SENSORS_NUMBER = 8
LIGHT_SENSORS_NUMBER = 8
MAX_SPEED = 4
 
OBSTACLE_THRESHOLD = 200       # ps reading above this = obstacle close
WALL_THRESHOLD = 250           # front sensors triggered = at the wall
GAP_THRESHOLD = 150            # side sensor drop = gap/hole detected
LIGHT_THRESHOLD_RATIO = 0.1    # fraction difference to trigger a turn toward light
 
# States for the wall-crossing behaviour
EXPLORE = "EXPLORE"
WALL_FOLLOW = "WALL_FOLLOW"
RECRUIT = "RECRUIT"
ATTRACTED = "ATTRACTED"
CROSSING = "CROSSING"
PHOTOTAXIS = "PHOTOTAXIS"
 
# initialization
robot = Robot()
name = robot.getName()
timestep = int(robot.getBasicTimeStep())
 
# get devices
distance_sensors = []
for i in range(DISTANCE_SENSORS_NUMBER):
    distance_sensors.append(robot.getDevice('ps' + str(i)))
    distance_sensors[i].enable(timestep)
 
light_sensors = []
for i in range(LIGHT_SENSORS_NUMBER):
    light_sensors.append(robot.getDevice('ls' + str(i)))
    light_sensors[i].enable(timestep)
 
# get motors
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)
 
# get communication devices (range limited to 1 m via the emitter's
# "range" field in the .wbt file -- this is the swarm recruitment channel)
emitter = robot.getDevice('emitter')
receiver = robot.getDevice('receiver')
receiver.enable(timestep)
 
# spread robots along the wall by alternating follow side based on name
wall_side = 1 if hash(name) % 2 == 0 else -1
 
state = EXPLORE
stuck_steps = 0
STUCK_STEP_LIMIT = int(3000 / timestep)  # ~3 seconds before giving up on a spot
 
# main loop
while robot.step(timestep) != -1:
    # read sensors
    ps_values = [distance_sensors[i].getValue() for i in range(DISTANCE_SENSORS_NUMBER)]
    ls_values = [light_sensors[i].getValue() for i in range(LIGHT_SENSORS_NUMBER)]
 
    front = ps_values[0] + ps_values[7]
    left_side = ps_values[5] + ps_values[6]
    right_side = ps_values[1] + ps_values[2]
    front_blocked = front > WALL_THRESHOLD
 
    # check for recruitment signals from nearby robots (stigmergic recruitment:
    # a robot that finds a hole broadcasts it, nearby robots get attracted)
    best_strength = 0.0
    best_direction = None
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
 
    print(f"{name}: state={state}, front={front:.1f}, left={left_side:.1f}, right={right_side:.1f}")
 
    if state == EXPLORE:
        if front_blocked:
            state = WALL_FOLLOW
        elif best_direction is not None:
            state = ATTRACTED
        else:
            # Braitenberg-style obstacle avoidance / random wander
            if front > OBSTACLE_THRESHOLD:
                # back up while turning so the robot actually clears the
                # obstacle instead of just pivoting in place against it
                left_speed = -0.3 * MAX_SPEED
                right_speed = 0.1 * MAX_SPEED
            elif left_side > OBSTACLE_THRESHOLD:
                left_speed = 0.5 * MAX_SPEED
                right_speed = 0.1 * MAX_SPEED
            elif right_side > OBSTACLE_THRESHOLD:
                left_speed = 0.1 * MAX_SPEED
                right_speed = 0.5 * MAX_SPEED
            else:
                left_speed += random.uniform(-0.2, 0.2) * MAX_SPEED
                right_speed += random.uniform(-0.2, 0.2) * MAX_SPEED
 
    elif state == WALL_FOLLOW:
        side_reading = left_side if wall_side > 0 else right_side
        if front_blocked:
            # back away from the wall while turning, so the robot actually
            # clears the obstacle instead of pivoting against it forever
            left_speed = -0.2 * MAX_SPEED - 0.2 * MAX_SPEED * wall_side
            right_speed = -0.2 * MAX_SPEED + 0.2 * MAX_SPEED * wall_side
            stuck_steps += 1
            if stuck_steps > STUCK_STEP_LIMIT:
                state = EXPLORE
                stuck_steps = 0
        elif side_reading < GAP_THRESHOLD:
            # gap detected next to us -> candidate hole
            state = RECRUIT
            stuck_steps = 0
        else:
            stuck_steps = 0
            base = 0.3 * MAX_SPEED
            correction = 0.1 * MAX_SPEED
            left_speed = base - correction * wall_side
            right_speed = base + correction * wall_side
 
    elif state == RECRUIT:
        emitter.send(f"HOLE:{name}".encode('utf-8'))
        left_speed = 0.4 * MAX_SPEED
        right_speed = 0.4 * MAX_SPEED
        state = CROSSING
 
    elif state == ATTRACTED:
        if best_direction is not None:
            dx, dz = best_direction[0], best_direction[2]
            angle = math.atan2(dx, dz)
            turn = max(-1.0, min(1.0, angle))
            left_speed = 0.5 * MAX_SPEED * (1 - turn)
            right_speed = 0.5 * MAX_SPEED * (1 + turn)
        else:
            state = EXPLORE
        if front_blocked:
            state = WALL_FOLLOW
 
    elif state == CROSSING:
        # push through the hole, avoiding collisions with queued robots
        if front > OBSTACLE_THRESHOLD:
            # back off slightly while turning instead of pivoting in place
            # against a queued robot ahead
            left_speed = -0.2 * MAX_SPEED
            right_speed = 0.1 * MAX_SPEED
        else:
            left_speed = 0.5 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED
        if max(ls_values) > 0:
            state = PHOTOTAXIS
 
    elif state == PHOTOTAXIS:
        # follow the light source on the right side of the arena
        reference_light_value = (ls_values[0] + ls_values[7]) / 2
        right_light_value = sum(ls_values[0:4]) / 4
        left_light_value = sum(ls_values[4:8]) / 4
        threshold = LIGHT_THRESHOLD_RATIO * reference_light_value
        if reference_light_value - left_light_value > threshold:
            left_speed = -0.3 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED
        elif reference_light_value - right_light_value > threshold:
            left_speed = 0.5 * MAX_SPEED
            right_speed = 0.3 * MAX_SPEED
        else:
            left_speed = 0.5 * MAX_SPEED
            right_speed = 0.5 * MAX_SPEED
 
    # set motor speeds
    left_speed = max(-MAX_SPEED, min(MAX_SPEED, left_speed))
    right_speed = max(-MAX_SPEED, min(MAX_SPEED, right_speed))
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)