import cv2
import time
import requests
import json
import sys
import subprocess

# Access command-line arguments
cameraIP = sys.argv[1]

#get motherboard id
try:
    # Execute dmidecode command and capture the output
    output = subprocess.check_output(["sudo","dmidecode", "-s", "baseboard-serial-number"], universal_newlines=True)
    motherboardID = output.strip()
    # print("Motherboard *ID* found *", motherboardID,"*")
except subprocess.CalledProcessError:
    # Handle any error that may occur
    print("Failed to retrieve motherboard ID")
    exit(1)


# Create a dictionary with the payload data
payload = {
    "mid": motherboardID,
    "cip": cameraIP
}

# Make the GET request with the payload
response_json = requests.get("http://localhost:4040/check_license/", data=json.dumps(payload), headers={"Content-Type": "application/json"})

# Check the response_json status code
if response_json.status_code == 200:
    response = response_json.json()
    if response["license"] == "valid":
        print("License valid: ", cameraIP)
    else:
        print("License/IP not valid! EXIT")
        exit(1)
else:
    # Request failed
    print("Request failed with status code: ",response_json.status_code)
    exit(1)



def boxNtag(frame, x,y,w,h, tag, font, color):
    # Draw a rectangle around the detected object
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    # Write the tag on the rectangle
    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
    text_x = x + int((w - text_size[0]) / 2)
    text_y = y - 10
    cv2.putText(frame, tag, (text_x, text_y), font, 0.9, color, 2)


with open("./cam_config.json") as file:
    cam_config = json.load(file)
    # print(cam_config)

#start camera feed
cam_feed = cv2.VideoCapture(cameraIP)

while True:

    ret, frame = cam_feed.read()

    # Check if we successfully read a frame
    if not ret:
        print("Camera ", cameraIP," failed to estabilish feed")
        break


    # Create a color specific mask to extract only BGR color pixels
    b = cam_config["blue_bounds"]
    g = cam_config["green_bounds"]
    r = cam_config["red_bounds"]
    masks=[] #BGR
    masks.append(cv2.inRange(frame, (b[0], b[1], b[2]), (b[3], b[4], b[5]))) #Blue
    masks.append(cv2.inRange(frame, (g[0], g[1], g[2]), (g[3], g[4], g[5]))) #Green
    masks.append(cv2.inRange(frame, (r[0], r[1], r[2]), (r[3], r[4], r[5]))) #Red


    #render machine boundary boxes for machins assigned to this camera
    for machine in cam_config["machines"]:
        if machine["assigned_cam"]==cameraIP:
            x1,y1,x2,y2 = machine["detect_boundary"]
            boxNtag(frame, x1,y1,x2-x1,y2-y1,machine["name"], cv2.FONT_HERSHEY_SIMPLEX, (100,255,100))


    #check all 3 colors of BGR spectrum
    for i in range(len(masks)):

        # Perform a series of morphological operations to remove noise
        # masks[i] = cv2.erode(masks[i], None, iterations=1)
        # masks[i] = cv2.dilate(masks[i], None, iterations=1)

        # Find contours of colored objects in the masks[1]
        contours, _ = cv2.findContours(masks[i].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for currentContour in contours:

            # Get the bounding rectangle of the largest contour
            x, y, w, h = cv2.boundingRect(currentContour)
            centerX = x+(w/2)
            centerY = y+(h/2)

            for machine in cam_config["machines"]:

                x1,y1,x2,y2 = machine["detect_boundary"]
                w_min,h_min= machine["minimum_size_detect"]
            
                if w > w_min and h > h_min and x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
                    boxNtag(frame, x,y,w,h,machine["name"], cv2.FONT_HERSHEY_SIMPLEX, (0,255,0))
        # masks[i] = cv2.resize(masks[i], (700, 350))

        # print("Checked mask",i)

    # cv2.imshow("Mask Blue", masks[0])
    # cv2.imshow("Mask Green", masks[1])
    # cv2.imshow("Mask Red", masks[2])

    # Resize the frame and masks[1]
    frame = cv2.resize(frame, (700, 350))

    # Display the original frame and the masks[1]
    camName = "CAM: " + cameraIP
    cv2.imshow(camName, frame)
    

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam_feed.release()
        cv2.destroyAllWindows()

    


