import numpy as np
import cv2
from math import pow, sqrt

lower = {'red': [(0, 100, 100),(161,100,100)], 'green': [(50, 50, 120),(0,0,0)], 'blue': [(100, 50, 50),(0,0,0)], }         #adding parameters for color recognition
upper = {'red': [(10, 255, 255),(179,255,255)], 'green': [(70, 255, 255),(0,0,0)], 'blue': [(130, 255, 255),(0,0,0)]}       #adding parameters for color recognition        
colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0)}                                                             #adding parameters for color circles 

green = [0, 0]                             #enemy coordinates
blue = [0, 0]                              #friend coordinates
distance = 0                               #distance between enemy and friend
green_past = [0, 0]                        #enemy past coordinates
blue_past = [0, 0]                         #friend past coordinates
speed_green = 0                            #speed in pixels per second
speed_blue = 0
frame = 0                                  #frame counter

webcam = cv2.VideoCapture(0)
            
while(True):
    _,imageFrame = webcam.read()
    frame += 1
    hsvFrame = cv2.cvtColor(imageFrame,cv2.COLOR_BGR2HSV)             #transfering image from BGR to HSV

    for key,value in upper.items():

        lower1 = np.array(lower[key][0], dtype="uint8")             #defining first lower mask
        upper1 = np.array(upper[key][0], dtype="uint8")             #defining first higher mask
        lower2 = np.array(lower[key][1], dtype="uint8")             #defining second lower mask
        upper2 = np.array(upper[key][1], dtype="uint8")             #defining second higher mask

        mask1 = cv2.inRange(hsvFrame, lower1, upper1)
        mask2 = cv2.inRange(hsvFrame, lower2, upper2)
        mask = mask1 + mask2
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
        output = cv2.bitwise_and(imageFrame, imageFrame, mask=mask)             #isolating preffered color from the image frame

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]        
        if (len(cnts) > 0):
            c = max(cnts, key=cv2.contourArea)      
            ((x, y), radius) = cv2.minEnclosingCircle(c)                #defining a circle with a minimal radius around the found object
            if radius > 10:
                cv2.circle(imageFrame, (int(x), int(y)), int(radius), colors[key], 2)      #drawing a circle round the found object
            #    cv2.line(imageFrame, (320, 240), (int(x), int(y)), colors[key], 2)         #drawing a line from the center of the frame to the circle

            if key == 'green':
                cv2.putText(imageFrame, 'Neprijatelj', (int(x) - int(radius) // 2, int(y) - int(radius) - 20),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, colors[key], 1)
                green[0] = int(x)                                                              #saving enemy coordinates
                green[1] = int(y)

            if key == 'blue':
                blue[0] = int(x)                                                             #saving friend coordinates
                blue[1] = int(y)


            speed_blue = str(30 * int(sqrt(pow((blue[0] - blue_past[0]), 2) + pow((blue[1] - blue_past[1]), 2))))
            speed_blue = '{} p/s'.format(speed_blue)
            speed_green = str(30 * int(sqrt(pow((green[0] - green_past[0]), 2) + pow((green[1] - green_past[1]), 2))))
            speed_green = '{} p/s'.format(speed_green)

            blue_past[0] = blue[0]                                                          #remember present coordinates as past
            blue_past[1] = blue[1]
            green_past[0] = green[0]
            green_past[1] = green[1]


            #if frame % 5 == 0:                                                             #sending every n frames
            print('enemy speed is {}, and friend speed is {}'.format(speed_green, speed_blue))
            #    cv2.putText(imageFrame, speed, (blue_x-int(radius/2), blue_y + int(radius+20)), cv2.FONT_HERSHEY_TRIPLEX, 0.5, colors['red'], 1)

            distance = int(sqrt(pow((green[0] - blue[0]), 2) + pow((green[1] - blue[1]), 2)))       #calculating distance between enemy and friend using coordinates
            if distance < (3 * radius):                                                             #if the distance is too small do something
                cv2.putText(imageFrame, 'STOP!', (blue[0] - int(radius / 2), blue[1] + int(radius + 20)),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, colors['red'], 3)
                #print('STOP!')


    cv2.imshow("images", np.hstack([imageFrame, output]))       #only able to shut down using q
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
webcam.release()
cv2.destroyAllWindows()
