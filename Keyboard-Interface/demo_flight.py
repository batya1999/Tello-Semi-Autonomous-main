# from numpy import imag
# from Aruco_detection import ArucoDetection
# from Tello_video import FileVideoStreamTello
from socket import *
from djitellopy import tello
from threading import Thread
# import cv2
from math import atan2, cos, sin, sqrt, pi
import numpy as np
import keyboard
from logger import Logger                  

class MinimalSubscriber():

    def __init__(self):

        # start the keyboard thread
        self.log = Logger("log1.csv")
        self.command = "stand"
        self.keyboard_thread = Thread(target=self.keyboard_control)
        
        self.log_thread = Thread(target=self.log_update)

        # connect to the Drone
        self.me = tello.Tello()
        self.me.connect()   

        # prints the Battery percentage
        print("Battery percentage:", self.me.get_battery())
        

        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attemp to takeoff due to low Battery")

        self.keyboard_thread.start()
        # print("index:", cur_index)
        print("Yaw:", self.me.get_yaw())
        print("height:", self.me.get_height())
        print("Barometer:",  self.me.get_barometer())
        print("Battery:", self.me.get_battery())
        print("X:", self.me.get_acceleration_x())
        print("Y:", self.me.get_acceleration_y())
        print("Z:", self.me.get_acceleration_z())
        
        

    def keyboard_control(self):
        """
            This method allows the user to control 
            its drone using the keyboard.
            'space' - takeoff / land
            'b' - battery
            'e' - emergancy
            'up' - Up
            'down' - Down
            'left' - left
            'right' - right
            'w' - Forawrd
            's' - Backward
            'a/d' - YAW (ANGLE/DIRECTION) 
        """
        big_factor = 100
        medium_factor = 50
        tookoff = False
        prev_index = 0
        cur_index = 0

        while True:
            cur_index += 1
            if cur_index>prev_index+30:
                prev_index = cur_index
                print("index:", cur_index)
                print("Yaw:", self.me.get_yaw())
                print("height:", self.me.get_height())
                print("Barometer:",  self.me.get_barometer())
                print("Battery:", self.me.get_battery())
                print("X:", self.me.get_acceleration_x())
                print("Y:", self.me.get_acceleration_y())
                print("Z:", self.me.get_acceleration_z())
             
            a, b, c, d = 0, 0, 0, 0
            self.command = "stand"

            # Takeoff 
            if keyboard.is_pressed('space') and not tookoff:
                tookoff = True
                self.me.takeoff()
                self.command = "takeoff"
            # Land
            if keyboard.is_pressed('space') and tookoff:
                tookoff = False
                self.me.land()
                self.command = "land"
            
            # Emergency
            if keyboard.is_pressed('e'):
                try:
                    print("EMERGENCY")
                    self.me.emergency()
                except Exception as e:
                    print("Did not receive OK, reconnecting to Tello")
                    self.me.connect()
            
            
            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                if tookoff:
                    self.me.land()
                break
            # Up / Down
            if keyboard.is_pressed('up'):
                c = 0.5 * medium_factor
                self.command = "UP"
            if keyboard.is_pressed("down"):
                c = -0.5 * medium_factor
                self.command = "DOWN"
            
            # Left / Right
            if keyboard.is_pressed('left'):
                a = -0.5 * big_factor
                self.command = "LEFT"
            if keyboard.is_pressed('right'):
                a = 0.5 * big_factor
                self.command = "RIGHT"
            
            # Forward / Backward
            if keyboard.is_pressed('w'):
                b = 0.5 * big_factor
                self.command = "FORWARD"
            if keyboard.is_pressed('s'):
                b = -0.5 * big_factor
                self.command = "BACKWARD"
            
            # YAW
            if keyboard.is_pressed('a'):
                d = -0.5 * big_factor
                self.command = "YAW LEFT"
            if keyboard.is_pressed('d'):
                d = 0.5 * big_factor
                self.command = "YAW RIGHT"
            
            # Save log
            # if keyboard.is_pressed('m'):
            #     self.log.save_log()
                # print("Log saved successfully!")
            
            # send the commands to the drone
            self.log.save_log()
            self.me.send_rc_control(int(a), int(b), int(c), int(d))


    def log_update(self):
        """   
            Update the state of the drone into the log file.
        """
        while True:
            state: dict = self.me.get_current_state()
            if len(state) == 21:
                self.log.add(state, self.command, self.frame_counter)
               

if __name__ == '__main__':
    tello = MinimalSubscriber()