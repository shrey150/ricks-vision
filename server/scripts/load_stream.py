import cv2

# Path to the video file
video_path = "../data/ricks-stream.ts"

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video was opened successfully
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Read and display frames
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If the frame was not retrieved, break the loop
    if not ret:
        print("End of video stream or error.")
        break

    # Display the resulting frame
    cv2.imshow('Video Frame', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
