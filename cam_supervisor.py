import cv2
import time
import requests
import json
import sys
import subprocess

# Access command-line arguments
camera = json.loads(sys.argv[1])

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


# Dict with the payload data
payload = {
    "mid": motherboardID,
    "cip": camera["ip"]
}

# Make the GET request with the payload
response_json = requests.get("http://localhost:4040/check_license/", data=json.dumps(payload), headers={"Content-Type": "application/json"})

print("Checking License...")
# Check the response_json status code
if response_json.status_code == 200:
    response = response_json.json()
    if response["license"] == "valid":
        print("Valid: ", camera["ip"])
    else:
        print("NOT valid: ", camera["ip"])
        exit(1)
else:
    # Request failed
    print("Request failed with status code: ",response_json.status_code)
    exit(1)



def machineTags(frame, x,y,w,h, tag, font, color):
    # Draw a rectangle around the detected object
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    # Write the tag on the rectangle
    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
    text_x = x + int((w - text_size[0]) / 2)
    text_y = y + h + (text_size[1]*2) - 10
    cv2.putText(frame, tag, (text_x, text_y), font, 0.9, color, 2)


def signalTags(frame, x,y,w,h, tag, font, color):
    # Draw a rectangle around the detected object
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    # Write the tag on the rectangle
    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
    text_x = x + int((w - text_size[0]) / 2)
    text_y = y - 10
    cv2.putText(frame, tag, (text_x, text_y), font, 0.9, color, 2)

def maskBoundaries(frame, b, option):
    if option == "BGR":
        return cv2.inRange(frame, (b[0], b[1], b[2]), (b[3], b[4], b[5]))
    elif option == "HSV":
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        if b[0]<0 or b[3]<0:
            mask1 = cv2.inRange(hsv, (179+b[0], b[1], b[2]), (179, b[4], b[5]))
            mask2 = cv2.inRange(hsv, (0, b[1], b[2]), (b[3], b[4], b[5]))
            return cv2.bitwise_or(mask1, mask2)
        else:
            return cv2.inRange(hsv, (b[0], b[1], b[2]), (b[3], b[4], b[5]))


def haasLogic(frame, machine, color):            
    x1,y1,x2,y2 = machine["detect_boundary"]
    w_min,h_min= machine["minimum_size_detect"]

    #if a signal was detected within the boundary of any machine
    if w > w_min and h > h_min and x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
        if color == 0:
            signalTags(frame, x1,y1,x2-x1,y2-y1,"RUNNING", cv2.FONT_HERSHEY_SIMPLEX, (0,255,0))
        elif color == 1:
            signalTags(frame, x1,y1,x2-x1,y2-y1,"MAINTANENCE", cv2.FONT_HERSHEY_SIMPLEX, (0,255,255))
        elif color == 2:
            signalTags(frame,x1,y1,x2-x1,y2-y1,"ERROR", cv2.FONT_HERSHEY_SIMPLEX, (0,0,255))
    

def fanucLogic(frame, machine, color):
    x1,y1,x2,y2 = machine["detect_boundary"]
    w_min,h_min= machine["minimum_size_detect"]
     #if a signal was detected within the boundary of any machine
    if w > w_min and h > h_min and x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
        if color == 0:
            signalTags(frame, x1,y1,x2-x1,y2-y1,"STOPPED", cv2.FONT_HERSHEY_SIMPLEX, (0,255,0))
        elif color == 1:
            signalTags(frame, x1,y1,x2-x1,y2-y1,"RUNNING", cv2.FONT_HERSHEY_SIMPLEX, (0,255,255))
        elif color == 2:
            signalTags(frame,x1,y1,x2-x1,y2-y1,"ERROR", cv2.FONT_HERSHEY_SIMPLEX, (0,0,255))
        

   
    




with open("./cam_config.json") as file:
    cam_config = json.load(file)

current_cam_machines=[]

# only use the machines relavent to this camera
for machine in cam_config["machines"]:
    if machine["assigned_cam"] ==  camera["ip"]:
        current_cam_machines.append(machine)

#start camera feed
cam_feed = cv2.VideoCapture(camera["ip"])

while True:

    ret, frame = cam_feed.read()

    # Check if we successfully read a frame
    if not ret:
        print("Camera ", camera["ip"]," failed to estabilish feed")
        break


    # Create a color specific mask to extract only BGR color pixels
    # note: this determins order of colors
    masks=[]
    masks.append(maskBoundaries(frame, cam_config["green_bounds"], cam_config["option"])) #find green signal 
    masks.append(maskBoundaries(frame, cam_config["yellow_bounds"], cam_config["option"])) #find yellow signal 
    masks.append(maskBoundaries(frame, cam_config["red_bounds"], cam_config["option"])) #find red signal 
   


    #render machine boundary boxes for machines assigned to this camera
    for machine in current_cam_machines:
        x1,y1,x2,y2 = machine["detect_boundary"]
        machineTags(frame, x1,y1,x2-x1,y2-y1,machine["name"], cv2.FONT_HERSHEY_SIMPLEX, (0,0,0))


    #check all 3 colors of GYR spectrum
    contours=[]
    for color in range(len(masks)):

        # Perform a series of morphological operations to remove noise
        masks[color] = cv2.erode(masks[color], None, iterations=cam_config["filter_iterations"])
        masks[color] = cv2.dilate(masks[color], None, iterations=cam_config["filter_iterations"])

        # Find contours of colored objects in the masks[1]
        raw_contours, _ = cv2.findContours(masks[color].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in raw_contours:
            if cv2.contourArea(cnt) > camera["minimum_area_detect"]:
                contours.append(cnt)

        masks[color] = cv2.resize(masks[color], (700, 350))

    for currentContour in contours:

        # Get the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(currentContour)
        centerX = x+(w/2)
        centerY = y+(h/2)

        signalTags(frame,x,y,w,h,"?", cv2.FONT_HERSHEY_SIMPLEX, (255,255,0))

        for machine in current_cam_machines:
            w_min,h_min= machine["minimum_size_detect"]
            if w > w_min and h > h_min and x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
                signalTags(frame,x,y,w,h,"detect", cv2.FONT_HERSHEY_SIMPLEX, (255,0,0))
    
            if machine["type"] == "HAAS":
                haasLogic(frame, machine, color)
            elif machine["type"] == "FANUC":
                fanucLogic(frame, machine, color)




    cv2.imshow("Mask Green", masks[0])
    cv2.imshow("Mask Yellow", masks[1])
    cv2.imshow("Mask Red", masks[2])

    # Resize the frame and masks[1]
    frame = cv2.resize(frame, (700, 350))

    # Display the original frame and the masks[1]
    camName = "CAM: " + camera["ip"]
    cv2.imshow(camName, frame)
    

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam_feed.release()
        cv2.destroyAllWindows()

    


