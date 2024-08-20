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
        'b' - battery status
        'e' - emergency
        'up' - Up
        'down' - Down
        'left' - Left
        'right' - Right
        'w' - Forward
        's' - Backward
        'a/d' - YAW (Angle/Direction) 
        'p' - Move forward for 1 second, hover for 1 second, and land
        'esc' - Exit the program
        """
        big_factor = 100
        medium_factor = 50
        tookoff = False

        while True:
            a, b, c, d = 0, 0, 0, 0
            self.command = "stand"

            if keyboard.is_pressed('space') and not tookoff:
                tookoff = True
                self.me.takeoff()
                self.command = "takeoff"
            elif keyboard.is_pressed('space') and tookoff:
                tookoff = False
                self.me.land()
                self.command = "land"
            elif keyboard.is_pressed('b'):
                print("Battery percentage:", self.me.get_battery())
            elif keyboard.is_pressed('e'):
                try:
                    print("EMERGENCY")
                    self.me.emergency()
                except Exception as e:
                    print("Did not receive OK, reconnecting to Tello")
                    self.me.connect()
            elif keyboard.is_pressed('up'):
                c = 0.5 * medium_factor
                self.command = "UP"
            elif keyboard.is_pressed("down"):
                c = -0.5 * medium_factor
                self.command = "DOWN"
            elif keyboard.is_pressed('left'):
                d = -0.5 * big_factor
                self.command = "LEFT"
            elif keyboard.is_pressed('right'):
                d = 0.5 * big_factor
                self.command = "RIGHT"
            elif keyboard.is_pressed('w'):
                b = 0.5 * big_factor
                self.command = "FORWARD"
            elif keyboard.is_pressed('s'):
                b = -0.5 * big_factor
                self.command = "BACKWARD"
            elif keyboard.is_pressed('a'):
                a = -0.5 * big_factor
                self.command = "YAW LEFT"
            elif keyboard.is_pressed('d'):
                a = 0.5 * big_factor
                self.command = "YAW RIGHT"
            elif keyboard.is_pressed('m'):
                self.log.save_log()
                print("Log saved successfully!")
            elif keyboard.is_pressed('p'):
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
            elif keyboard.is_pressed('esc'):
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
