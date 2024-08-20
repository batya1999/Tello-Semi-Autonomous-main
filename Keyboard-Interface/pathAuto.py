from numpy import imag
from Aruco_detection import ArucoDetection
from Tello_video import FileVideoStreamTello
from socket import *
from djitellopy import tello
from threading import Thread
import cv2
from math import atan2, cos, sin, sqrt, pi
import numpy as np
import keyboard
from logger import Logger
import time  # Import time module for delays



def keyboard_control(self):
    """
        This method allows the user to control 
        its drone using the keyboard.
        'space' - takeoff / land   
        'b' - battery
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

        # Takeoff 
        if keyboard.is_pressed('space') and not tookoff:
            tookoff = True
            self.me.takeoff()
            self.command = "takeoff"
        # Land
        elif keyboard.is_pressed('space') and tookoff:
            tookoff = False
            self.me.land()
            self.command = "land"
        # Battery
        elif keyboard.is_pressed('b'):
            print("Battery percentage:", self.me.get_battery())
        
        # Emergency
        elif keyboard.is_pressed('e'):
            try:
                print("EMERGENCY")
                self.me.emergency()
            except Exception as e:
                print("Did not receive OK, reconnecting to Tello")
                self.me.connect()

        # Up / Down
        elif keyboard.is_pressed('up'):
            c = 0.5 * medium_factor
            self.command = "UP"
        elif keyboard.is_pressed("down"):
            c = -0.5 * medium_factor
            self.command = "DOWN"
        
        # Left / Right
        elif keyboard.is_pressed('left'):
            d = -0.5 * big_factor
            self.command = "LEFT"
        elif keyboard.is_pressed('right'):
            d = 0.5 * big_factor
            self.command = "RIGHT"
        
        # Forward / Backward
        elif keyboard.is_pressed('w'):
            b = 0.5 * big_factor
            self.command = "FORWARD"
        elif keyboard.is_pressed('s'):
            b = -0.5 * big_factor
            self.command = "BACKWARD"
        
        # YAW
        elif keyboard.is_pressed('a'):
            a = -0.5 * big_factor
            self.command = "YAW LEFT"
        elif keyboard.is_pressed('d'):
            a = 0.5 * big_factor
            self.command = "YAW RIGHT"
        
        # Save log
        elif keyboard.is_pressed('m'):
            self.log.save_log()
            print("Log saved successfully!")
        
        # Fly forward, hover, and land with 'p'
        elif keyboard.is_pressed('p'):
            if not tookoff:
                self.me.takeoff()
                tookoff = True
            self.me.send_rc_control(0, 50, 0, 0)  # Fly forward
            self.command = "Fly forward"
            time.sleep(1)
            self.me.send_rc_control(0, 0, 0, 0)  # Hover
            self.command = "Hover"
            time.sleep(1)
            self.me.land()
            tookoff = False
            self.command = "land"
            print("Executed 'p' command: Forward, Hover, Land")

        # Exit with 'esc'
        elif keyboard.is_pressed('esc'):
            print("Exiting program.")
            if tookoff:
                self.me.land()
            break

        # Send the commands to the drone
        self.me.send_rc_control(int(a), int(b), int(c), int(d))

