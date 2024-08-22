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
# global target_point
# # target_point = (0, 0)

# def get_center_of_mask(frame: np.ndarray)->tuple:
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
#     cv2.circle(green_mask, (cent_x, cent_y), 10, (255, 255, 0), 2)

#     return cent_x, cent_y

# def update_target_point(x, y):
#     global target_point
#     target_point = (x, y)

# def select_point(event, x, y, flags, param):
#     global target_point
#     if event == cv2.EVENT_MOUSEMOVE:
#         update_target_point(x, y)

# def calculate_initial_coordinate_system(drone_point):
#     global target_point
#     # Calculate differences in x, y, and z coordinates
#     dy = target_point[0] - drone_point[0]
#     dx = target_point[1] - drone_point[1]

#     # Calculate the horizontal distance and the total distance including z
#     dist_horizontal = math.sqrt(dx ** 2 + dy ** 2)
#     #dist_total = math.sqrt(dist_horizontal ** 2 + dz ** 2)

#     # Calculate the horizontal angle in degrees
#     angle_radians = math.atan2(dy, dx)
#     angle_degrees = math.degrees(angle_radians)

#     if angle_radians < 0:
#         angle_degrees = -(angle_degrees + 180)
#     else:
#         angle_degrees = -(angle_degrees - 180)

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

#         self.keyboard_thread = Thread(target=self.keyboard_control)
#         self.log_thread = Thread(target=self.log_update)
#         self.video_thread = Thread(target=self.video)

#         if self.me.get_battery() < 10:
#             raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

#         self.keyboard_thread.start() 
#         self.log_thread.start()
#         self.video_thread.start()

#     def smooth_yaw_adjustment(self, target_yaw):
#         """
#         Adjusts the drone's yaw smoothly towards the target yaw angle.
#         """
#         current_yaw = self.me.get_yaw()
#         yaw_speed = 0.1  # Smaller increments for smoother yaw

#         while abs(target_yaw - current_yaw) > 1:  # Adjust tolerance as needed
#             if target_yaw > current_yaw:
#                 self.me.send_rc_control(0, 0, 0, int(yaw_speed * 100))
#             elif target_yaw < current_yaw:
#                 self.me.send_rc_control(0, 0, 0, int(-yaw_speed * 100))

#             time.sleep(0.1)
#             current_yaw = self.me.get_yaw()

#         # Stop yaw movement after reaching the desired angle
#         self.me.send_rc_control(0, 0, 0, 0)
        
#         # Start moving forward slowly after yaw adjustment is complete
#         print("Yaw adjustment complete. Moving forward slowly.")
#         self.me.send_rc_control(0, 20, 0, 0)  # Adjust forward speed as needed
#         time.sleep(2)  # Move forward for 2 seconds (adjust as needed)
#         self.me.send_rc_control(0, 0, 0, 0)  # Stop forward movement

#     def keyboard_control(self):
#         """
#         Allows the user to control the drone using the keyboard.
#         """
#         global target_point
#         target_point = (0, 0)

#         big_factor = 100
#         medium_factor = 50
#         tookoff = False

#         cap = cv2.VideoCapture(1)
#         cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)

#         # Window
#         combined_window_name = "Track Mouse and Detect Green Light"
#         cv2.namedWindow(combined_window_name, cv2.WINDOW_AUTOSIZE)
#         cv2.setMouseCallback(combined_window_name, select_point)

#         last_calculation_time = time.time()  # Initialize the last calculation time
#         while True:
#             current_time = time.time()
#             if keyboard.is_pressed('esc'):
#                 self.me.land()
#                 self.command = "land"
#                 break
#             #radar:
#             angle_degrees = 0

#             cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)
#             ret, frame = cap.read()
#             if frame is None:
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#                 continue

#             image = frame.copy()
#             drone_loc = get_center_of_mask(image)
#             if drone_loc is not None and current_time - last_calculation_time >= 0.1:
#                 print("distance: ", calculate_distance(drone_loc, target_point))
#                 print("drone_loc", drone_loc, "target_point", target_point)
#                 if calculate_distance(target_point, drone_loc) <= 10 and tookoff:
#                     self.me.land()
#                     self.command = "land"
#                 cv2.circle(image, drone_loc, 10, (255, 255, 0), 2)
#                 angle_degrees = int(calculate_initial_coordinate_system(drone_loc))
#             else:
#                 # todo: calc 
#                 pass

#             print(angle_degrees)

#             cv2.imshow(combined_window_name, image)

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

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
#             if (-5 <= angle_degrees <= 5) and tookoff:
#                 b = 0.5 * big_factor
#                 self.command = "FORWARD"
#             if keyboard.is_pressed('s'):
#                 b = -0.5 * big_factor
#                 self.command = "BACKWARD"
#             if (angle_degrees < -5) and tookoff:
#                 target_yaw = angle_degrees
#                 self.smooth_yaw_adjustment(target_yaw)
#                 self.command = "YAW LEFT"
#             if (angle_degrees > 5) and tookoff:
#                 target_yaw = angle_degrees
#                 self.smooth_yaw_adjustment(target_yaw)
#                 self.command = "YAW RIGHT"
#             if keyboard.is_pressed('p') and tookoff:
#                 try:
#                     print("Performing demo command...")
#                     self.me.send_rc_control(0, 50, 0, 0)
#                     time.sleep(1)
#                     self.me.send_rc_control(0, 0, 0, 0)
#                     self.me.land()
#                     break
#                 except Exception as e:
#                     print("Exception while performing demo command", str(e))
#                     self.me.land()
#             if keyboard.is_pressed('esc'):
#                 self.me.land()
#                 self.command = "land"
#                 break

#             self.me.send_rc_control(int(a), int(b), int(c), int(d))
#             # time.sleep(0.05)  # Short delay to control the command frequency

#         cap.release()
#         cv2.destroyAllWindows()

#     def video(self):
#         # self.me.streamon()
#         while True:
#             try:
#                 frame_read = self.me.get_frame_read()
#                 my_frame = frame_read.frame
#                 cv2.imshow("MyResult", my_frame)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#             except Exception as e:
#                 print(str(e))
#                 break

#         # self.me.streamoff()

#     def log_update(self):
#         while True:
#             time.sleep(0.2)
#             if self.command:
#                 self.log.log_command(self.command)
#                 print("Logged command:", self.command)


# if __name__ == '__main__':
#     MinimalSubscriber()


import cv2
import keyboard
import time
from threading import Thread
from djitellopy import tello
from logger import Logger
import numpy as np
import math
import time

# global target_points
global target_point
# target_point = (0, 0)

def get_center_of_mask(frame: np.ndarray) -> tuple:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((10, 10), np.uint8)
    dilate = cv2.dilate(green_mask, kernel)

    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None

    cent_x = int(M["m10"] / M["m00"])
    cent_y = int(M["m01"] / M["m00"])

    cv2.imshow("mask", green_mask)
    cv2.circle(green_mask, (cent_x, cent_y), 10, (255, 255, 0), 2)

    return cent_x, cent_y

def update_target_point(x, y):
    global target_point
    target_point = (x, y)

def select_point(event, x, y, flags, param):
    global target_point
    if event == cv2.EVENT_MOUSEMOVE:
        update_target_point(x, y)

def calculate_initial_coordinate_system(drone_point):
    global target_point
    dy = target_point[0] - drone_point[0]
    dx = target_point[1] - drone_point[1]

    dist_horizontal = math.sqrt(dx ** 2 + dy ** 2)

    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    if angle_radians < 0:
        angle_degrees = -(angle_degrees + 180)
    else:
        angle_degrees = -(angle_degrees - 180)

    return angle_degrees

def calculate_distance(point1, point2):
    if point1 is not None and point2 is not None:
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    else:
        return 10000
    return distance

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
        self.log_thread = Thread(target=self.log_update)
        self.video_thread = Thread(target=self.video)

        if self.me.get_battery() < 10:
            raise RuntimeError("Tello rejected attempt to takeoff due to low battery")

        self.keyboard_thread.start() 
        self.log_thread.start()
        self.video_thread.start()

    def smooth_yaw_adjustment(self, target_yaw):
        current_yaw = self.me.get_yaw()
        yaw_speed = 0.1  # Smaller increments for smoother yaw

        while abs(target_yaw - current_yaw) > 1:
            if target_yaw > current_yaw:
                self.me.send_rc_control(0, 0, 0, int(yaw_speed * 100))
            elif target_yaw < current_yaw:
                self.me.send_rc_control(0, 0, 0, int(-yaw_speed * 100))

            time.sleep(0.1)
            current_yaw = self.me.get_yaw()

        self.me.send_rc_control(0, 0, 0, 0)
        print("Yaw adjustment complete. Moving forward slowly.")
        
    def keyboard_control(self):
        global target_point
        target_point = (0, 0)

        big_factor = 100
        medium_factor = 50
        tookoff = False

        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)

        combined_window_name = "Track Mouse and Detect Green Light"
        cv2.namedWindow(combined_window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(combined_window_name, select_point)

        last_calculation_time = time.time()
        while True:
            current_time = time.time()
            if keyboard.is_pressed('esc'):
                self.me.land()
                self.command = "land"
                break

            angle_degrees = 0

            cap.set(cv2.CAP_PROP_BRIGHTNESS, -64)
            ret, frame = cap.read()
            if frame is None:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            image = frame.copy()
            drone_loc = get_center_of_mask(image)
            if drone_loc is not None and current_time - last_calculation_time >= 0.1:
                print("distance: ", calculate_distance(drone_loc, target_point))
                print("drone_loc", drone_loc, "target_point", target_point)
                if calculate_distance(target_point, drone_loc) <= 10 and tookoff:
                    self.me.land()
                    self.command = "land"
                cv2.circle(image, drone_loc, 10, (255, 255, 0), 2)
                angle_degrees = int(calculate_initial_coordinate_system(drone_loc))
            else:
                pass

            print(angle_degrees)

            cv2.imshow(combined_window_name, image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

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
                b = 0.2 * big_factor
                self.command = "FORWARD"
            if keyboard.is_pressed('s'):
                b = -0.2 * big_factor
                self.command = "BACKWARD"
            if (angle_degrees < -5) and tookoff:
                target_yaw = angle_degrees
                self.smooth_yaw_adjustment(target_yaw)
                b = 0.5 * big_factor  # Move forward after yaw adjustment
                self.command = "YAW LEFT"
            if (angle_degrees > 5) and tookoff:
                target_yaw = angle_degrees
                self.smooth_yaw_adjustment(target_yaw)
                b = 0.5 * big_factor  # Move forward after yaw adjustment
                self.command = "YAW RIGHT"
            if keyboard.is_pressed('p') and tookoff:
                try:
                    print("Performing demo command...")
                    self.me.send_rc_control(0, 50, 0, 0)
                    time.sleep(1)
                    self.me.send_rc_control(0, 0, 0, 0)
                    self.me.land()
                    break
                except Exception as e:
                    print("Exception while performing demo command", str(e))
                    self.me.land()
            if keyboard.is_pressed('esc'):
                self.me.land()
                self.command = "land"
                break

            self.me.send_rc_control(int(a), int(b), int(c), int(d))

        cap.release()
        cv2.destroyAllWindows()

    def video(self):
        while True:
            if keyboard.is_pressed('esc'):
                self.me.land()
                break
            self.img = self.me.get_frame_read().frame
            img = cv2.resize(self.img, (360, 240))
            cv2.imshow("Drone Camera", img)
            cv2.waitKey(1)

    def log_update(self):
        while True:
            if self.command == "land":
                self.log.add_log("Drone landed")
                break
            self.log.add_log(self.command)
            time.sleep(0.1)


if __name__ == "__main__":
    minimal_subscriber = MinimalSubscriber()
