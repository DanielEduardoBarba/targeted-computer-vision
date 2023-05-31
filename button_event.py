import cv2

# Button event function
def button_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if 50 <= x <= 150 and 50 <= y <= 100:
            print("Button 1 Pressed")
        elif 200 <= x <= 300 and 50 <= y <= 100:
            print("Button 2 Pressed")

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Create a window and set the button event callback
cv2.namedWindow("Video")
cv2.setMouseCallback("Video", button_event)

while True:
    # Read the frame from the video capture
    ret, frame = cap.read()

    # Draw buttons on the frame
    cv2.rectangle(frame, (50, 50), (150, 100), (0, 255, 0), -1)
    cv2.putText(frame, "Button 1", (60, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.rectangle(frame, (200, 50), (300, 100), (0, 0, 255), -1)
    cv2.putText(frame, "Button 2", (210, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    # Display the frame
    cv2.imshow("Video", frame)

    # Check for keyboard input
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()
