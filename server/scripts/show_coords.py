import cv2
import numpy as np

# get project root
import os
import sys

# Load the uploaded image
image = cv2.imread("../data/ricks-frame.jpg")

# Store clicked points
points = []
drawing_image = image.copy()

# Mouse callback function
def get_cursor_position(event, x, y, flags, param):
    global drawing_image, points
    
    if event == cv2.EVENT_MOUSEMOVE:  # Detect mouse movement
        temp_image = drawing_image.copy()
        if len(points) > 0:
            # Draw line from last point to current mouse position
            cv2.line(temp_image, points[-1], (x,y), (0,255,0), 2)
        cv2.imshow("Rick's Frame", temp_image)
        
    elif event == cv2.EVENT_LBUTTONDOWN:  # Detect left mouse click
        print(f"Left Click at: x={x}, y={y}")
        points.append((x,y))
        # Draw point
        cv2.circle(drawing_image, (x,y), 5, (0,0,255), -1)
        # Draw line if there are at least 2 points
        if len(points) > 1:
            cv2.line(drawing_image, points[-2], points[-1], (0,255,0), 2)
        cv2.imshow("Rick's Frame", drawing_image)
        
    elif event == cv2.EVENT_RBUTTONDOWN:  # Detect right mouse click
        print(f"Right Click at: x={x}, y={y}")
        # Reset
        points.clear()
        drawing_image = image.copy()
        cv2.imshow("Rick's Frame", drawing_image)

# Create a window and set the mouse callback
cv2.namedWindow("Rick's Frame")
cv2.setMouseCallback("Rick's Frame", get_cursor_position)

# Display the image and wait for interaction
while True:
    cv2.imshow("Rick's Frame", drawing_image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Press 'q' to exit
        break
    elif key == 27:  # Press ESC to clear points
        points.clear()
        print("\n")
        drawing_image = image.copy()
        cv2.imshow("Rick's Frame", drawing_image)

# Clean up
cv2.destroyAllWindows()
