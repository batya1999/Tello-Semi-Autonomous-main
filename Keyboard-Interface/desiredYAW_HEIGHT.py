import time
from djitellopy import tello
from threading import Thread
from logger import Logger

class MinimalSubscriber:

    def __init__(self):

        # start the keyboard thread
        self.log = Logger("log1.csv")
        self.command = "stand"

        # Connect to the Drone
        self.me = tello.Tello()
        self.me.connect()

        # Prints the Battery percentage
        print("Battery percentage:", self.me.get_battery())

        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

        # Example usage with desired height and yaw
        desired_height = 100  # Example: 100 cm
        desired_yaw = self.me.get_yaw() + 90  # Example: 90 degrees

        self.takeoff_and_set_position(desired_height, desired_yaw)

    def takeoff_and_set_position(self, desired_height, desired_yaw):
        """
        Takes off, then rotates the drone to the desired yaw angle, and hovers at the desired height.
        """
        # Takeoff
        self.me.takeoff()
        print("Taking off...")
        time.sleep(0.1)

        # Set desired height
        while self.me.get_height() < desired_height:
            self.me.send_rc_control(0, 0, 50, 0)  # Move upward
            time.sleep(0.1)
        self.me.send_rc_control(0, 0, 0, 0)  # Stop upward movement
        print(f"Reached desired height: {desired_height} cm")

        # Rotate to desired yaw
        current_yaw = self.me.get_yaw()
        yaw_speed = 20  # Yaw speed, you can adjust this value

        while abs(current_yaw - desired_yaw) > 1:  # Small tolerance for reaching exact yaw
            if desired_yaw > current_yaw:
                self.me.send_rc_control(0, 0, 0, yaw_speed)
            else:
                self.me.send_rc_control(0, 0, 0, -yaw_speed)
            time.sleep(0.1)
            current_yaw = self.me.get_yaw()

        self.me.send_rc_control(0, 0, 0, 0)  # Stop rotation
        print(f"Reached desired yaw: {desired_yaw} degrees")

        # Hold position
        self.command = "hover"
        while True:
            # Hover at current position
            self.me.send_rc_control(0, 0, 0, 0)
            time.sleep(0.1)

    def log_update(self):
        """   
        Update the state of the drone into the log file.
        """
        while True:
            state = self.me.get_current_state()
            if len(state) == 21:
                self.log.add(state, self.command, 0)

if __name__ == '__main__':
    tello = MinimalSubscriber()
