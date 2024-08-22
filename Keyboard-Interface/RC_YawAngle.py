
# import cv2
# import keyboard
# import time
# from threading import Thread
# from djitellopy import tello
# from logger import Logger
# import numpy as np
# import math
# import time

# # global target_points
# global target_point ,y_size
# # target_point = (0, 0)

# def get_center_of_mask(frame: np.ndarray)->tuple:
#     global y_size
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     lower_green = np.array([40, 100, 100])
#     upper_green = np.array([80, 255, 255])

#     green_mask = cv2.inRange(hsv, lower_green, upper_green)
#     # Dilate the mask
#     kernel = np.ones((10, 10), np.uint8)
#     dilate = cv2.dilate(green_mask, kernel)

#     # Find contours
      
#     contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


#     if len(contours) == 0:
#         return None

#     # Find the largest contour
#     largest_contour = max(contours, key=cv2.contourArea)

#     # Compute the moments of the largest contour
#     M = cv2.moments(largest_contour)
#     if M["m00"] == 0:
#         return None

#     # Calculate the center of the contour
#     cent_x = int(M["m10"] / M["m00"])
#     cent_y = int(M["m01"] / M["m00"])

#     cv2.imshow("mask", green_mask)

#     cv2.circle(green_mask, (cent_x,y_size - cent_y), 10, (255, 255, 0), 2)


#     return cent_x, y_size - cent_y

# def update_target_point(x, y):
#     global target_point, y_size
#     target_point = (x, y_size - y)
# def select_point(event, x, y, flags, param):
#     global target_point, y_size
#     if event == cv2.EVENT_MOUSEMOVE:
#         update_target_point(x, y_size - y)

# def calculate_initial_coordinate_system(drone_point, target_point):
#     # Calculate differences in x, y
#     dy = drone_point[0] - target_point[0]
#     dx = drone_point[1] - target_point[1]

#     # Calculate the horizontal distance and the total distance
#     dist_horizontal = math.sqrt(dx ** 2 + dy ** 2)
#     #dist_total = math.sqrt(dist_horizontal ** 2 + dz ** 2)

#     # Calculate the horizontal angle in degrees
#     angle_radians = math.atan2(dx, dy)
#     #angle_radians = math.atan2(dy, dx)
#     angle_degrees = math.degrees(angle_radians)

#     if angle_radians < 0:
#         angle_degrees = (angle_degrees + 180)
#     else:
#         angle_degrees = (angle_degrees - 180)

#     return angle_degrees

# def calculate_distance(point1, point2):
#     if point1 is not None and point2 is not None:
#         x1, y1 = point1
#         x2, y2 = point2
#         distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#     else:
#         return 10000
#     return distance



# class MinimalSubscriber:

#     def __init__(self):
#         self.log = Logger("log1.csv")
#         self.command = "stand"
#         self.frame_counter = 0
        
#         self.me = tello.Tello()
#         self.me.connect()
#         self.img = None

#         print("Battery percentage:", self.me.get_battery())

#         # #self.streamQ = FileVideoStreamTello(self.me)

#         self.keyboard_thread = Thread(target=self.keyboard_control)
#         #self.log_thread = Thread(target=self.log_update)
#         #self.video_thread = Thread(target=self.video)

#         if self.me.get_battery() < 10:
#             raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

#         self.keyboard_thread.start() 
#         #self.streamQ.start()
#         #self.video_thread.start()

#     def keyboard_control(self):
#         """
#         Allows the user to control the drone using the keyboard.
#         'space' - takeoff / land   
#         'b' - battery status
#         'e' - emergency
#         'up' - Up
#         'down' - Down
#         'left' - Left
#         'right' - Right
#         'w' - Forward
#         's' - Backward
#         'a/d' - YAW (Angle/Direction) 
#         'p' - Move forward for 1 second, hover for 1 second, and land
#         'esc' - Exit the program
#         """
#         global target_point, y_size
#         target_point = (0, 0)

#         big_factor = 100
#         medium_factor = 50
#         tookoff = False
#         yaw_val = 0.1

#         # cap = cv2.VideoCapture(1)
#         # cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)

#         # # Window
#         # combined_window_name = "Track Mouse and Detect Green Light"
#         # cv2.namedWindow(combined_window_name, cv2.WINDOW_AUTOSIZE)
#         # cv2.setMouseCallback(combined_window_name, select_point)
#         angle_degrees = 15
#         last_calculation_time = time.time()  # Initialize the last calculation time
#         while True:
#             current_time = time.time()
#             self.me.get_yaw()

#             #radar:
              

#             # cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)
#             # ret, frame = cap.read()
#             # y_size = frame.shape[1]
#             # if frame is None:
#             #     if cv2.waitKey(1) & 0xFF == ord('q'):
#             #         break
#             #     continue

#             # image = frame.copy()
#             # drone_loc = get_center_of_mask(image)
#             # if drone_loc is not None and  current_time - last_calculation_time >= 0.1:
               
#             #     print("distance: ",calculate_distance(drone_loc,target_point))
#             #     #print("drone_loc", drone_loc, "target_point", target_point)
#             #     if calculate_distance(target_point, drone_loc)<=10 and tookoff:
#             #         self.me.land()
#             #         self.command = "land"
#             #     cv2.circle(image, (drone_loc[0],y_size -drone_loc[1]), 10, (255, 255, 0), 2)
#             #     angle_degrees = int(calculate_initial_coordinate_system(drone_loc, target_point))
#             #     print("angle_degrees",angle_degrees)
              
               
#             # else:
#             #     # todo: calc 
#             #     pass


#             # cv2.imshow(combined_window_name, image)

#             # if cv2.waitKey(1) & 0xFF == ord('q'):
#             #     break

#             a, b, c, d = 0, 0, 0, 0
#             self.command = "stand"

           
#             if keyboard.is_pressed('space') and not tookoff:
#                 tookoff = True
#                 self.me.takeoff()
#                 self.command = "takeoff"
#             if keyboard.is_pressed('space') and tookoff:
#                 tookoff = False
#                 self.me.land()
#                 self.command = "land"
#             if keyboard.is_pressed('b'):
#                 print("Battery percentage:", self.me.get_battery())
#             if keyboard.is_pressed('e'):
#                 try:
#                     print("EMERGENCY")
#                     self.me.emergency()
#                 except Exception as e:
#                     print("Did not receive OK, reconnecting to Tello")
#                     self.me.connect()
#             if keyboard.is_pressed('up'):
#                 c = 0.5 * medium_factor
#                 self.command = "UP"
#             if keyboard.is_pressed("down"):
#                 c = -0.5 * medium_factor
#                 self.command = "DOWN"      
#             if keyboard.is_pressed('left'):
#                 a = -0.5 * big_factor
#                 self.command = "LEFT"
#             if keyboard.is_pressed('right'):
#                 a = 0.5 * big_factor
#                 self.command = "RIGHT"
#             if (-5<=angle_degrees<=5) and tookoff:
#                 self.me.get_yaw()
#                 b = 0.5 * big_factor
#                 self.command = "FORWARD"
#                 print("FORWARD")
#             if keyboard.is_pressed('s'):
               
#                 b = -0.5 * big_factor
#                 self.command = "BACKWARD"
                
#             if (angle_degrees<-5) and tookoff: 
#                 self.me.get_yaw()
#                 # d = -yaw_val * big_factor
#                 self.me.rotate_clockwise(angle_degrees)
#                 angle_degrees = 0    
#                 # print("YAW LEFT")
#                 #b = 0.5 * big_factor 
#                 self.command = "YAW LEFT"
#                 print("YAW LEFT")
#             if (angle_degrees>5) and tookoff:
#                 self.me.get_yaw()
#                 # d = yaw_val * big_factor
#                 #b = 0.5 * big_factor
#                 self.me.rotate_clockwise(angle_degrees)
#                 angle_degrees = 0   
#                 self.command = "YAW RIGHT"
#                 print("YAW RIGHT")
#             if keyboard.is_pressed('m'):
#                 self.log.save_log()
#                 print("Log saved successfully!")
#             if keyboard.is_pressed('p'):
#                 if not tookoff:
#                     self.me.takeoff()
#                     tookoff = True
#                 self.me.send_rc_control(0, 50, 0, 0)  # Fly forward
#                 self.command = "Fly forward"
#                 time.sleep(3)
#                 self.me.send_rc_control(0, 0, 0, 0)  # Hover
#                 self.command = "Hover"
#                 time.sleep(2)  
#                 self.me.land()
#                 tookoff = False
#                 self.command = "land"
#                 print("Executed 'p' command: Forward, Hover, Land")
#             if keyboard.is_pressed('esc'):
#                 print("Exiting program.")
#                 if tookoff:
#                     self.me.land()
#                 break

#             self.me.send_rc_control(int(a), int(b), int(c), int(d))

#         #cap.release()
#         #cv2.destroyAllWindows()

#     def log_update(self):
#         """
#         Update the state of the drone into the log file.
#         """
#         while True:
#             state = self.me.get_current_state()
#             if len(state) == 21:
#                 self.log.add(state, self.command, self.frame_counter)

#     def video(self):
#         """
#         Captures and displays the video from the drone.
#         """
#         while True:
#             try:
#                 img = self.streamQ.read()
#                 self.frame_counter += 1
#                 self.img = img
#             except Exception:
#                 break
            
#             cv2.imshow("TelloView", self.img)
#             cv2.waitKey(1)

# if __name__ == '__main__':
#     tello = MinimalSubscriber()


import cv2
import keyboard
import time
from threading import Thread
from djitellopy import tello
from logger import Logger
import numpy as np
import math
import time

# Global variables
global target_point, y_size
target_point = (0, 0)
initial_yaw = None
yaw_limit_reached = False

class MinimalSubscriber:

    def __init__(self):
        self.log = Logger("log1.csv")
        self.command = "stand"
        self.frame_counter = 0

        self.me = tello.Tello()
        self.me.connect()
        self.img = None

        print("Battery percentage:", self.me.get_battery())

        self.keyboard_thread = Thread(target=self.keyboard_control)

        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

        self.keyboard_thread.start()

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
        global target_point, y_size, initial_yaw, yaw_limit_reached

        big_factor = 100
        medium_factor = 50
        tookoff = False
        yaw_speed = 0.2  # Yaw speed (degrees per update)
        desired_angle = 10  # Desired yaw adjustment angle
        angle_degrees = 0

        while True:
            current_yaw = self.me.get_yaw()  # Get the current yaw

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
            if (-5 <= angle_degrees <= 5) and tookoff:
                b = 0.5 * big_factor
                self.command = "FORWARD"
                print("FORWARD")
            if keyboard.is_pressed('s'):
                b = -0.5 * big_factor
                self.command = "BACKWARD"

            if (angle_degrees < -5) and tookoff:
                if initial_yaw is None:
                    initial_yaw = current_yaw

                if abs(current_yaw - initial_yaw) < desired_angle and not yaw_limit_reached:
                    d = -yaw_speed * big_factor
                    self.command = "YAW LEFT"
                    print("YAW LEFT")
                else:
                    yaw_limit_reached = True

            if (angle_degrees > 5) and tookoff:
                if initial_yaw is None:
                    initial_yaw = current_yaw

                if abs(current_yaw - initial_yaw) < desired_angle and not yaw_limit_reached:
                    d = yaw_speed * big_factor
                    self.command = "YAW RIGHT"
                    print("YAW RIGHT")
                else:
                    yaw_limit_reached = True

            if not keyboard.is_pressed('a') and not keyboard.is_pressed('d'):
                initial_yaw = None
                yaw_limit_reached = False

            if keyboard.is_pressed('m'):
                self.log.save_log()
                print("Log saved successfully!")
            # if keyboard.is_pressed('p'):
            #     if not tookoff:
            #         self.me.takeoff()
            #         tookoff = True
            #     self.me.send_rc_control(0, 50, 0, 0)  # Fly forward
            #     self.command = "Fly forward"
            #     time.sleep(3)
            #     self.me.send_rc_control(0, 0, 0, 0)  # Hover
            #     self.command = "Hover"
            #     time.sleep(2)
            #     self.me.land()
            #     tookoff = False
            #     self.command = "land"
            #     print("Executed 'p' command: Forward, Hover, Land")
            if keyboard.is_pressed('esc'):
                print("Exiting program.")
                if tookoff:
                    self.me.land()
                break

            self.me.send_rc_control(int(a), int(b), int(c), int(d))

if __name__ == '__main__':
    tello = MinimalSubscriber()
