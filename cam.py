import cv2
import time
import requests
import json

with open("./cam_data.json") as file:
    cam_config = json.load(file)

# Define the lower and upper boundaries of the yellow color in HSV
color_lower = (45, 50, 50)
color_upper = (65, 255, 255)

# Start capturing video from the default webcam
cap = cv2.VideoCapture(0)

while True:
    # time.sleep(1)
    # Read a frame from the video stream
    ret, frame = cap.read()

    # Check if we successfully read a frame
    if not ret:
        break

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask to extract only ccolor pixels
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # Perform a series of morphological operations to remove noise
    mask = cv2.erode(mask, None, iterations=0)
    mask = cv2.dilate(mask, None, iterations=0)

    # Find contours of yellow objects in the mask
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours are found
    if len(contours) > 0:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        if w > 50 and h > 50:
            # Draw a rectangle around the detected object
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            centerX = x+(w/2)
            centerY = y+(h/2)

            if centerX > 300:
                print("RIGHT")
                response = requests.post("http://localhost:4040",json={"sig1":centerY}, headers={"Content-Type": "application/json"})
                print(response)
            if centerX < 300:
                print("LEFT")


    # Display the original frame and the mask
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()


