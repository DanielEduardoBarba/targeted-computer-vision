import cv2
import requests
import json
import sys
import subprocess
from datetime import datetime
import time

# Access command-line arguments
camera = json.loads(sys.argv[1])

with open("./cam_config.json") as file:
    cam_config = json.load(file)

with open('cam_events.json', 'r') as file:
    cam_events = json.load(file)

#delay between logs to prevent spamming of data, in seconds
logBufferDelay = 3

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
    "feed_url": camera["feed_url"]
}

# Make the GET request with the payload
response_json = requests.get("http://localhost:4040/check_license", data=json.dumps(payload), headers={"Content-Type": "application/json"})

print("Checking License...")
# Check the response_json status code
if response_json.status_code == 200:
    response = response_json.json()
    if response["license"] == "valid":
        print("Valid: ", camera["feed_url"])
    else:
        print("NOT valid: ", camera["feed_url"])
        exit(1)
else:
    # Request failed
    print("Request failed with status code: ",response_json.status_code)
    exit(1)


# move camera to position
# requests.get("http://admin:admin@"+camera["ip"]+":80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=1&-act=home&-speed=1", headers={"Content-Type": "application/json"})
# print("Homing camera...")
# time.sleep(35)
# print("OK!")
  
# for movement in camera["cam_position"]:
#     # Make the GET request with the payload
#     print("Moving ", movement,"..." )
#     response_json = requests.get("http://admin:admin@"+camera["ip"]+":80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=1&-act="+movement+"&-speed=1", headers={"Content-Type": "application/json"})
 
#     # Check the response_json status code
#     if response_json.status_code == 200:
#         print("OK!")
#     else:
#         print("Move failed with status code: ",response_json.status_code) 



def machineTags(frame, x,y,w,h, tag, font, color):
    # Draw a rectangle around the detected object
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
    # Write the tag on the rectangle
    text_size, _ = cv2.getTextSize(tag, font, 0.9, 2)
    text_x = x + int((w - text_size[0]) / 2)
    text_y = y + h + (text_size[1]*2) - 10
    cv2.putText(frame, tag, (text_x, text_y), font, 1.1, color, 3)


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

def callAPI(machine, status):
    for machine_event in cam_events["machine_events"]: 
        if machine_event["last_event"] != status and logBufferDelay< int(time.time())-int(machine_event["event_time_seconds"]) and machine_event["id"]==machine["id"]:
            machine_event["last_event"]=status
            machine_event["event_time"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            machine_event["event_time_seconds"]=int(time.time())
            payload = {
                "machine_event": machine_event,
                "machine": machine
            }

            response_json=requests.post("http://localhost:4040/singlefeed", data=json.dumps(payload), headers={"Content-Type": "application/json"})
            # Check the response_json status code
            if response_json.status_code == 200:
                response = response_json.json()
                if response["response"] == "OK!":
                    
                    with open('cam_events.json', 'w') as file:
                        json.dump(cam_events, file)

                    print("Status: ", machine["name"] ," ",status," logged")
                else:
                    print("Data wasn't saved to DB properly")
                
            else:
                # Request failed
                print("Request and process failed with status code: ",response_json.status_code)


def haasLogic(frame, machine, color, contours):            
    x1,y1,x2,y2 = machine["detect_boundary"]
    min_w,min_h = machine["minimum_size_detect"]
    for currentContour in contours:
        # Mark detected areas (suspected signal)
        x, y, w, h = cv2.boundingRect(currentContour)
        centerX=x+(w/2)
        centerY=y+(h/2)

        status="OFF"
        status_color=(0,0,0)
        
        if w > min_w and h > min_h:
            signalTags(frame,x,y,w,h,"detected", cv2.FONT_HERSHEY_SIMPLEX, (255,255,0))
            if x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
                if color == 0:
                    status="RUNNING"
                    status_color=(0,255,0)
                    # print("COLOR 0")
                elif color == 1:
                    status="MAINTANENCE"
                    status_color=(0,255,255)
                    # print("COLOR 1")
                elif color == 2:
                    status="ERROR"
                    status_color=(0,0,255)
                    # print("COLOR 2")
            
                signalTags(frame,x1,y1,x2-x1,y2-y1,status, cv2.FONT_HERSHEY_SIMPLEX, status_color)
                callAPI(machine, status)
    callAPI(machine, "OFF")

    

def fanucLogic(frame, machine, color, contours):
    x1,y1,x2,y2 = machine["detect_boundary"]
    min_w,min_h = machine["minimum_size_detect"]
    for currentContour in contours:
        # Mark detected areas (suspected signal)
        x, y, w, h = cv2.boundingRect(currentContour)
        centerX=x+(w/2)
        centerY=y+(h/2)

        status="OFF"
        status_color=(0,0,0)
        
        if w > min_w and h > min_h:
            signalTags(frame,x,y,w,h,"detected", cv2.FONT_HERSHEY_SIMPLEX, (255,255,0))
            if x1 < centerX and y1 < centerY and x2 > centerX and y2> centerY:
            
                if color == 0:
                    status="STOPPED"
                    status_color=(0,255,0)
                elif color == 1:
                    status="RUNNING"
                    status_color=(0,255,255)
                elif color == 2:
                    status="ERROR"
                    status_color=(0,0,255)

                signalTags(frame,x1,y1,x2-x1,y2-y1, status, cv2.FONT_HERSHEY_SIMPLEX, status_color)
                callAPI(machine, status)
    callAPI(machine, "OFF")


current_cam_machines=[]
# only use the machines relavent to this camera
for machine in cam_config["machines"]:
    if machine["assigned_cam_ip"] ==  camera["ip"]:
        current_cam_machines.append(machine)

#start camera feed
cam_feed = cv2.VideoCapture(camera["feed_url"])

while True:

    ret, frame = cam_feed.read()

    # Check if we successfully read a frame
    if not ret:
        print("Camera ", camera["feed_url"]," failed to estabilish feed")


    # Create a color specific mask to extract only BGR color pixels
    # note: this determins order of colors
    masks=[]
    masks.append(maskBoundaries(frame, cam_config[camera["view"]]["green_bounds"], camera["view"])) #find green signal 
    masks.append(maskBoundaries(frame, cam_config[camera["view"]]["yellow_bounds"], camera["view"])) #find yellow signal 
    masks.append(maskBoundaries(frame, cam_config[camera["view"]]["red_bounds"], camera["view"])) #find red signal 
   
    #render machine boundary boxes for machines assigned to this camera
    for machine in current_cam_machines:
        x1,y1,x2,y2 = machine["detect_boundary"]
        machineTags(frame, x1,y1,x2-x1,y2-y1,machine["name"], cv2.FONT_HERSHEY_SIMPLEX, machine["default_boundary_color"])

    #check all 3 colors of GYR spectrum
    contours=[]
    for color in range(len(masks)):

        # Perform a series of morphological operations to remove noise
        masks[color] = cv2.erode(masks[color], None, iterations=cam_config["filter_iterations"])
        masks[color] = cv2.dilate(masks[color], None, iterations=cam_config["filter_iterations"])

        # Find contours of colored objects in the masks[1]
        contours, _ = cv2.findContours(masks[color].copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

        for machine in current_cam_machines:

            if machine["type"] == "HAAS":
                haasLogic(frame, machine, color, contours)
            elif machine["type"] == "FANUC":
                fanucLogic(frame, machine, color, contours)
                            
        masks[color] = cv2.resize(masks[color], (700, 350))

    cv2.imshow("Mask Green "+camera["view"], masks[0])
    cv2.imshow("Mask Yellow" +camera["view"], masks[1])
    cv2.imshow("Mask Red "+camera["view"], masks[2])

    # Resize the frame and masks[1]
    frame = cv2.resize(frame, (1000, 500))

    # Display the original frame and the masks[1]
    camTitle = "View: " + camera["view"] +" CAM: " + camera["feed_url"] 
    cv2.imshow(camTitle, frame)
    

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam_feed.release()
        cv2.destroyAllWindows()

    


