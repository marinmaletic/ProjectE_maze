#! /usr/bin/env python3
import sys
import rospy
import cv2
import numpy as np
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import matplotlib.pyplot as plt
import time
import PPPKod as testing
import maze_solver as ms
#import maze_solver as ms

class DroneControl:
    def __init__(self):
        self.__cv_bridge=CvBridge()
        rospy.init_node("Drone_controller", anonymous=True)
        self.camera_pub = rospy.Publisher("/bebop/camera_control", Twist, queue_size=10)
        
        self.img=None
        #cv2.startWindowThread()
        #cv2.namedWindow('drone image')
        rospy.Rate(25)
        t = Twist()
        t.angular.y = -90
        current_time = rospy.get_time()
        while rospy.get_time()-current_time<6.:
            self.camera_pub.publish(t)
            
        self.camera_sub = rospy.Subscriber("/bebop/image_raw", Image, self.get_image)
        
        rospy.spin()

    def get_image(self, img_msg):

        
        imageFrame=self.__cv_bridge.imgmsg_to_cv2(img_msg, desired_encoding="bgr8") # Needs to be checked
        
        

        cv2.imshow('drone image', imageFrame)
        
        pts1 = np.array(0)
        while pts1.shape !=(4,2):
            try:
                pts1 = testing.izracunaj_koordinate_vrhova(imageFrame)
               
            except Exception as e:
                print(e)
                return

             
            pts1 = np.array(pts1)
            #plt.imshow(imageFrame)
            #plt.show()
            
        pts1 = np.array(pts1)
        print(f"Points to transform: {pts1}")
        pts2 = np.float32([[0, 0], [0, 650], [650, 0],  [650, 650] ])
        M = cv2.getPerspectiveTransform(pts1.astype(np.float32),pts2)

        new_img = cv2.warpPerspective(imageFrame, M, (650, 650))
        new_img = cv2.flip(new_img, 1)
        cv2.imshow("transformirano", new_img)

        
        grayImage = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
        (thresh, blackAndWhiteImage) = cv2.threshold(grayImage,90, 255, cv2.THRESH_BINARY)
        maze_image = new_img
        edges = cv2.Canny(blackAndWhiteImage,0, 255,apertureSize = 3)
        minLineLength = 100
        maxLineGap = 5
        lines = cv2.HoughLinesP(edges,1,np.pi/180,10, minLineLength, maxLineGap)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(maze_image, (x1, y1), (x2, y2), (0, 0, 0), 4)
        plt.figure(figsize=(7,7))
        plt.imshow(blackAndWhiteImage) # show the image on the screen 
        plt.show()

        # TODO Maze solving
        #simplified_maze = ms.simplify(blackAndWhiteImage)
        ms.find_path(blackAndWhiteImage)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyAllWindows()
        



    
  
if __name__ == "__main__":
    x = DroneControl()
    