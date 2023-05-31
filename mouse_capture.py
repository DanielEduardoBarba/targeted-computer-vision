import cv2

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Left button clicked at position (x={}, y={})".format(x, y))

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

# Create a window and set the mouse callback
cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_callback)

while True:
    # Read the frame from the video capture
    ret, frame = cap.read()

    # Display the frame
    cv2.imshow("Video", frame)

    # Check for keyboard input
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()
