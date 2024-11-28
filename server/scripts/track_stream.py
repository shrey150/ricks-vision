import cv2
import numpy as np
import os
from tkinter import Tk, Scale, HORIZONTAL, Button, Label
import threading

# Load YOLO
net = cv2.dnn.readNet(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3", "yolov3.weights"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3", "yolov3.cfg")
)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load the video
cap = cv2.VideoCapture("../data/ricks-stream.ts")

# Initialize Tkinter
root = Tk()
root.title("Video Player")

# Video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Create a scale for scrubbing
scale = Scale(root, from_=0, to=total_frames - 1, orient=HORIZONTAL, length=500)
scale.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

# Bind the scale's movement to the update_frame function
scale.bind("<Motion>", lambda event: update_frame())

# Create a label to display information
info_label = Label(root, text="People: 0, Line Length: 0")
info_label.grid(row=1, column=0, padx=10, pady=10)

# Variable to track play/pause state
is_playing = False

# Define queue_box as a list of tuples representing the polygon's vertices
queue_box = [(564, 507), (470, 488), (816, 141), (869, 153)]  # Coordinates from user clicks

def point_in_polygon(x, y, polygon):
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def process_frame(frame_number):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        return None

    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    boxes, confidences, class_ids = [], [], []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:
                center_x, center_y, w, h = map(int, detection[:4] * [width, height, width, height])
                x, y = int(center_x - w / 2), int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    count_in_queue = 0

    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        # Check if person's center point is inside the polygon
        center_x = x + w//2
        center_y = y + h//2
        if point_in_polygon(center_x, center_y, queue_box):
            count_in_queue += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Draw queue region as a polygon
    points = np.array(queue_box, np.int32)
    points = points.reshape((-1, 1, 2))
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)
    
    return frame, count_in_queue, width


# Function to update the frame
def update_frame():
    frame_number = scale.get()
    result = process_frame(frame_number)
    if result is not None:
        frame, people_count, line_length = result

        # Display the frame
        cv2.imshow("Frame", frame)

        # Update the information label
        info_label.config(text=f"People: {people_count}, Line Length: {line_length}")

# Function to toggle play/pause state
def toggle_play_pause():
    global is_playing
    is_playing = not is_playing
    play_pause_button.config(text="Pause" if is_playing else "Play")

# Function to run OpenCV's imshow in a separate thread
def video_thread():
    while True:
        if is_playing:
            frame_number = scale.get()
            result = process_frame(frame_number)
            if result is not None:
                frame, people_count, line_length = result
                cv2.imshow("Frame", frame)
                cv2.waitKey(int(1000 / fps))  # Wait for the duration of one frame
                # Move to the next frame
                scale.set((frame_number + 1) % total_frames)

# Button to toggle play/pause
play_pause_button = Button(root, text="Play", command=toggle_play_pause)
play_pause_button.grid(row=2, column=0, padx=10, pady=10)

# Button to update the frame
update_button = Button(root, text="Update Frame", command=update_frame)
update_button.grid(row=1, column=1, padx=10, pady=10)

# Start the video thread
threading.Thread(target=video_thread, daemon=True).start()

# Main loop
root.mainloop()

cap.release()
cv2.destroyAllWindows()
