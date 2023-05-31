import cv2

# URL for the IP camera stream
# url = 'http://admin:admin@192.168.0.200/livestream.cgi?stream=11&action=play&media=video_audio_data'
url = 'rtsp://192.168.0.200/11'
# Create a VideoCapture object with the URL
cap = cv2.VideoCapture(url)

while True:
    # Read the frame from the video capture
    ret, frame = cap.read()

    if ret:
        # Display the frame
        cv2.imshow('IP Camera Stream', frame)

    # Check for keyboard input
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
cap.release()

# Close all windows
cv2.destroyAllWindows()
