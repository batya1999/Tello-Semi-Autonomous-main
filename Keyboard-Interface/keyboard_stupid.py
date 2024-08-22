from numpy import imag
from Tello_video import FileVideoStreamTello
from socket import *
from djitellopy import tello
from threading import Thread
import cv2
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

        
        

    def keyboard_control(self):
        """
            This method allows the user to control 
            its drone using the keyboard.
            'space' - takeoff / land
            'b' - battery
            'e' - emergency
            'up' - Up
            'down' - Down
            'left' - left
            'right' - right
            'w' - Forward
            's' - Backward
            'a/d' - YAW (ANGLE/DIRECTION) 
        """
        big_factor = 100
        medium_factor = 50
        tookoff = False
        prev_index = 0
        cur_index = 0
        desired_angle = 60
        yaw_speed = 0.2 * big_factor
        yaw_limit_reached = False
        initial_yaw = None

        while True:
            cur_index += 1
            if cur_index > prev_index + 100:
                prev_index = cur_index
                print("index:", cur_index)
                print("Yaw:", self.me.get_yaw())
                print("height:", self.me.get_height())
                print("Barometer:", self.me.get_barometer())
                print("Battery:", self.me.get_battery())
                print("X:", self.me.get_speed_x())
                print("Y:", self.me.get_speed_y())
            
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
            
            # YAW (Limit to 15 degrees)
            current_yaw = self.me.get_yaw()
            
            if keyboard.is_pressed('a'):
                if initial_yaw is None:
                    initial_yaw = current_yaw
                
                if abs(current_yaw - initial_yaw) < desired_angle and not yaw_limit_reached:
                    d = -yaw_speed
                    self.command = "YAW LEFT"
                else:
                    yaw_limit_reached = True
            
            elif keyboard.is_pressed('d'):
                if initial_yaw is None:
                    initial_yaw = current_yaw
                
                if abs(current_yaw - initial_yaw) < desired_angle and not yaw_limit_reached:
                    d = yaw_speed
                    self.command = "YAW RIGHT"
                else:
                    yaw_limit_reached = True
            
            else:
                initial_yaw = None
                yaw_limit_reached = False
            
            # Send the commands to the drone
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