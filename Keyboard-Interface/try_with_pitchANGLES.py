import cv2
import keyboard
import time
from threading import Thread
from djitellopy import tello
from logger import Logger

class MinimalSubscriber:

    def __init__(self):
        self.log = Logger("log1.csv")
        self.command = "stand"
        self.frame_counter = 0
         
        self.me = tello.Tello()
        self.me.connect()
        self.img = None

        print("Battery percentage:", self.me.get_battery())
  
        # self.streamQ = FileVideoStreamTello(self.me)

        self.keyboard_thread = Thread(target=self.keyboard_control)
        self.log_thread = Thread(target=self.log_update)
        self.video_thread = Thread(target=self.video)

        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

        self.keyboard_thread.start() 
        self.streamQ.start()
        self.video_thread.start()

    def keyboard_control(self):
        """
        Allows the user to control the drone using the keyboard.
        'space' - takeoff / land   
        'b' - battery status ddwa 
        'e' - emergency
        'up' - Up
        'down' - Down
        'left' - Left
        'right' - Right
        'w' - Forward
        's' - Backward
        'a/d' - YAW (Angle/Direction) 
        'p' - Move forward for 1 second, hover for 1 second, and land
        'g' - Execute a pre-defined automatic path
        'esc' - Exit the program
        """
        big_factor = 100
        medium_factor = 50
        yaw_val = 0.1
        yaw_30_degrees = 0.2 * big_factor
        yaw_15_degrees = 0.7 * big_factor

        tookoff = False

        while True:
            angle_degrees = 0
            a, b, c, d = 0, 0, 0, 0
            self.command = "stand"

            if keyboard.is_pressed('space') and not tookoff:
                tookoff = True
                self.me.takeoff()
                self.command = "takeoff"
            if keyboard.is_pressed('space') and tookoff:
                tookoff = False
                self.me.land()
                self.command = "land"
            if keyboard.is_pressed('b'):
                print("Battery percentage:", self.me.get_battery())
            if keyboard.is_pressed('e'):
                try:
                    print("EMERGENCY")
                    self.me.emergency()
                except Exception as e:
                    print("Did not receive OK, reconnecting to Tello")
                    self.me.connect()
            if keyboard.is_pressed('up'):
                c = 0.5 * medium_factor
                self.command = "UP"
            if keyboard.is_pressed("down"):
                c = -0.5 * medium_factor
                self.command = "DOWN"
            if keyboard.is_pressed('left'):
                a = -0.5 * big_factor
                self.command = "LEFT"
            if keyboard.is_pressed('right'):
                a = 0.5 * big_factor
                self.command = "RIGHT"
            if (-5<=angle_degrees<=5):
                b = 0.5 * big_factor
                self.command = "FORWARD"
            if keyboard.is_pressed('s'):
                b = -0.5 * big_factor
                self.command = "BACKWARD"
            if (angle_degrees<-5):
                # d = -yaw_val * big_factor
                self.me.rotate_clockwise(angle_degrees)
                self.command = "YAW LEFT"
            if (angle_degrees>5):
                # d = yaw_val * big_factor
                self.me.rotate_clockwise(angle_degrees)
                self.command = "YAW RIGHT"
            if keyboard.is_pressed('m'):
                self.log.save_log()
                print("Log saved successfully!")
            if keyboard.is_pressed('p'):
                if not tookoff:
                    self.me.takeoff()
                    tookoff = True
                self.me.send_rc_control(0, 50, 0, 0)  # Fly forward
                self.command = "Fly forward"
                time.sleep(3)
                self.me.send_rc_control(0, 0, 0, 0)  # Hover
                self.command = "Hover"
                time.sleep(2)  
                self.me.land()
                tookoff = False
                self.command = "land"
                print("Executed 'p' command: Forward, Hover, Land")
            if keyboard.is_pressed('g'):
                # Execute the automated path
                if not tookoff:
                    self.me.takeoff()
                    tookoff = True
                    self.command = "takeoff"
                time.sleep(0.5)

                # self.me.send_rc_control(0, 0, 0, int(yaw_30_degrees))  # Yaw right 30 degrees
                self.me.rotate_clockwise(180)
                # self.command = "YAW RIGHT 60 degrees"
                time.sleep(6)

                # self.me.send_rc_control(0, 0, 0, int(yaw_30_degrees))  # Yaw right 30 degrees
                # self.command = "YAW LEFT 60 degrees"
                # time.sleep(1)

                # self.me.send_rc_control(0, 50, 0, 0)  # Move forward for 1 second
                # self.command = "Move forward"
                # time.sleep(1)

                # self.me.send_rc_control(0, 0, 0, 0)  # Stop and hover for 0.5 seconds
                # self.command = "Hover"
                # time.sleep(0.5)

                # self.me.send_rc_control(0, 0, 0, int(-yaw_15_degrees))  # Yaw left 15 degrees
                # self.command = "YAW LEFT 15 degrees"
                # time.sleep(1)

                self.me.land()
                tookoff = False
                self.command = "land"
                print("Executed 'g' command: Auto Path")

            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                if tookoff:
                    self.me.land()
                break

            self.me.send_rc_control(int(a), int(b), int(c), int(d))

    def log_update(self):
        """
        Update the state of the drone into the log file.
        """
        while True:
            state = self.me.get_current_state()
            if len(state) == 21:
                self.log.add(state, self.command, self.frame_counter)

    def video(self):
        """
        Captures and displays the video from the drone.
        """
        while True:
            try:
                img = self.streamQ.read()
                self.frame_counter += 1
                self.img = img
            except Exception:
                break
            
            cv2.imshow("TelloView", self.img)
            cv2.waitKey(1)

if __name__ == '__main__':
    tello = MinimalSubscriber()
