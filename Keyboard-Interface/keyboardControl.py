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
import time

class MinimalSubscriber():

    def __init__(self):

        self.ARUCO_DICT = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,     # the one we use!
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
            "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
            "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
            "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
        }

        # start the keyboard thread
        self.log = Logger("log1.csv")
        self.command = "stand"
        self.frame_counter = 0
        self.keyboard_thread = Thread(target=self.keyboard_control)
        
        self.log_thread = Thread(target=self.log_update)

        # connect to the Drone
        self.me = tello.Tello()
        self.me.connect()   

        self.img = None

        # prints the Battery percentage
        print("Battery percentage:", self.me.get_battery())
        
        # create the video capture thread
        self.video_thread = Thread(target=self.video)
        # if the battery is too low its arise an error
        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attemp to takeoff due to low Battery")

        # Aruco detector
        # stream thread
        self.streamQ = FileVideoStreamTello(self.me)
        self.draw_thread = Thread(target=self.draw)


        self.keyboard_thread.start()
        # self.log_thread.start()
        self.streamQ.start()
        self.video_thread.start()
        # self.draw_thread.start()
        

    def keyboard_control(self):
        """
            This method allows the user to control 
            its drone using the keyboard.
            'space' - takeoff / land   ddddaaaaaaaaaaaaa 
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
                a = -0.5 * big_factor
                self.command = "LEFT"
            elif keyboard.is_pressed('right'):  
                a = 0.5 * big_factor
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
                d = -0.1 * big_factor
                self.command = "YAW LEFT"
            elif keyboard.is_pressed('d'):
                d = 0.1 * big_factor
                self.command = "YAW RIGHT"
            elif keyboard.is_pressed('g'):
                # Execute the automated path
                if not tookoff:
                    self.me.takeoff()
                    tookoff = True
                    self.command = "takeoff"
                time.sleep(0.5)

                # self.me.send_rc_control(0, 0, 0, int(yaw_30_degrees))  # Yaw right 30 degrees
                self.me.rotate_clockwise(15)
                # self.command = "YAW RIGHT 60 degrees"
                time.sleep(2)
                self.me.rotate_clockwise(-15)
                time.sleep(2)
                print(self.me.get_height())
                self.me.land() 
                
            
            # Save log
            elif keyboard.is_pressed('m'):
                self.log.save_log()
                print("Log saved successfully!")
            
            # send the commands to the drone
            print("height in cm is:", self.me.get_height())
            print("Baro value is:", self.me.get_barometer())
            self.me.send_rc_control(int(a), int(b), int(c), int(d)) # 


    def log_update(self):
        """
            Update the state of the drone into the log file.
        """
        while True:
            state: dict = self.me.get_current_state()
            if len(state) == 21:
                self.log.add(state, self.command, self.frame_counter)
                cv2.imwrite("frames/frame_"+str(self.frame_counter)+".jpg", self.img)
            


    def video(self):
        """
            This method detects Faces/Persons and Aruco Codes.
            It plot the video captured from the Drone and it's detected objects boundaries.
        """

        while True:
            try:
                img = self.streamQ.read()
                # wait for valid frame
                imghud = img.copy()
                self.aruco.set_image_to_process(img)
                self.ids, self.corners = self.aruco.draw_detection(img)
                self.frame_counter += 1
                self.img = imghud
                
            except Exception:
                break
            
            cv2.imshow("ArucoView",self.img)
            k = cv2.waitKey(1)

    def draw(self):
        while True:
            if self.img is not None:
                h,w = self.img.shape[:2]
                for id, coord in zip(self.ids, self.corners):
                        coord = coord.reshape((4,2))
                        cv2.putText(self.img, str(id), (int(w/2), int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

if __name__ == '__main__':
    tello = MinimalSubscriber()