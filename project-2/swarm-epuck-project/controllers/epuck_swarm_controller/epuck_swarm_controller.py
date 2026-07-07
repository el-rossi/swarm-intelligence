import sys
from controller import Robot

class EpuckSwarmController:
    def __init__(self):
        self.robot = Robot()
        self.timeStep = int(self.robot.getBasicTimeStep())
        self.position_sensor = self.robot.getPositionSensor('position sensor')
        self.position_sensor.enable(self.timeStep)
        self.light_sensor = self.robot.getLightSensor('light sensor')
        self.light_sensor.enable(self.timeStep)
        self.left_motor = self.robot.getMotor('left wheel motor')
        self.right_motor = self.robot.getMotor('right wheel motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.speed = 6.28

    def navigate(self):
        while self.robot.step(self.timeStep) != -1:
            light_value = self.light_sensor.getValue()
            if light_value > 0.5:  # Assuming a threshold for light detection
                self.move_forward()
            else:
                self.avoid_obstacle()

    def move_forward(self):
        self.left_motor.setVelocity(self.speed)
        self.right_motor.setVelocity(self.speed)

    def avoid_obstacle(self):
        self.left_motor.setVelocity(-self.speed)
        self.right_motor.setVelocity(self.speed)

if __name__ == "__main__":
    controller = EpuckSwarmController()
    controller.navigate()