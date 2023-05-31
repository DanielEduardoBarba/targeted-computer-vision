import cv2
import time
import requests
import json

with open("./cam_config.json") as file:
    cam_config = json.load(file)
    # print(cam_config)


# Start capturing video from the default webcam
cap = cv2.VideoCapture(cam_config["machines"][0]["rtsp"])

while True:
    # time.sleep(1)
    # Read a frame from the video stream
    ret, frame = cap.read()

    # Check if we successfully read a frame
    if not ret:
        break

    # Convert the frame to the HSV color space
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    masks=[1,2,3]
    # Create a color specific mask to extract only BGR color pixels
    masks[0] = cv2.inRange(frame, (240, 0, 0), (255, 240, 240)) #Blue
    masks[1] = cv2.inRange(frame, (0, 240, 0), (240, 255, 240)) #Green
    masks[2] = cv2.inRange(frame, (0, 0, 240), (240, 240, 255)) #Red


    for machine in cam_config["machines"]:

        x1,y1,x2,y2 = machine["detect_boundary"]
        w=x2-x1
        # Write the tag on the rectangle
        tag = machine["name"]
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
        text_x = x1 + int((w - text_size[0]) / 2)
        text_y = y1 - 10
        cv2.putText(frame, tag, (text_x, text_y), font, 0.9, (0, 255, 100), 2)

        #create detection frames from config file
        cv2.rectangle(frame, (x,y,x1,y1), (0, 255, 100), 2)

   
    #check all 3 colors of BGR spectrum
    for i in range(len(masks)):
        # Perform a series of morphological operations to remove noise
        masks[i] = cv2.erode(masks[i], None, iterations=1)
        masks[i] = cv2.dilate(masks[i], None, iterations=1)
        # Find contours of colored objects in the masks[1]
        contours, _ = cv2.findContours(masks[i].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for currentContour in contours:

            # Find the largest contour
            # largest_contour = max(contours, key=cv2.contourArea)

            # Get the bounding rectangle of the largest contour
            x, y, w, h = cv2.boundingRect(currentContour)
            centerX = x+(w/2)
            centerY = y+(h/2)

            for machine in cam_config["machines"]:

                x1,y1,x2,y2 = machine["detect_boundary"]
                w_min,h_min= machine["minimum_size_detect"]
            
                if w > w_min and h > h_min and x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
                    
                    # Draw a rectangle around the detected object
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    # Write the tag on the rectangle
                    tag = machine["name"]
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
                    text_x = x + int((w - text_size[0]) / 2)
                    text_y = y - 10
                    cv2.putText(frame, tag, (text_x, text_y), font, 0.9, (0, 255, 0), 2)


                    # if centerX > 300:
                    #     print("RIGHT")
                    #     # response = requests.post("http://localhost:4040",json={"sig1":centerY}, headers={"Content-Type": "application/json"})
                    #     # print(response)
                    # if centerX < 300:
                    #     print("LEFT")
        masks[i] = cv2.resize(masks[i], (700, 350))
        
        # print("Checked mask",i)

    cv2.imshow("Mask Blue", masks[0])
    cv2.imshow("Mask Green", masks[1])
    cv2.imshow("Mask Red", masks[2])
    # Resize the frame and masks[1]
    frame = cv2.resize(frame, (700, 350))

    # Display the original frame and the masks[1]
    cv2.imshow("Frame", frame)
    

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# EXIT and release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()


def boxNtag(frame, x,y,w,h, tag, font, color):
    # Draw a rectangle around the detected object
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    # Write the tag on the rectangle
    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
    text_x = x + int((w - text_size[0]) / 2)
    text_y = y - 10
    cv2.putText(frame, tag, (text_x, text_y), font, 0.9, color, 2)
