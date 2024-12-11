import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, BooleanVar

# Create tkinter window for controls first
root = tk.Tk()
root.title("Video Controls")

# Now we can create Tkinter variables
snap_enabled = BooleanVar(value=False)

# Load the video
video_path = "../data/ricks-stream.ts"
cap = cv2.VideoCapture(video_path)

# Video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Store clicked points
points = []
drawing_image = None
is_playing = False

# Mouse callback function
def get_cursor_position(event, x, y, flags, param):
    global drawing_image, points
    
    if event == cv2.EVENT_MOUSEMOVE:  # Detect mouse movement
        if drawing_image is not None:
            temp_image = drawing_image.copy()
            if len(points) > 0:
                # Draw line from last point to current mouse position
                cv2.line(temp_image, points[-1], (x,y), (0,255,0), 2)
            cv2.imshow("Video Frame", temp_image)
        
    elif event == cv2.EVENT_LBUTTONDOWN:  # Detect left mouse click
        print(f"Left Click at: x={x}, y={y}")
        points.append((x,y))
        # Draw point
        cv2.circle(drawing_image, (x,y), 5, (0,0,255), -1)
        # Draw line if there are at least 2 points
        if len(points) > 1:
            cv2.line(drawing_image, points[-2], points[-1], (0,255,0), 2)
        cv2.imshow("Video Frame", drawing_image)
        
    elif event == cv2.EVENT_RBUTTONDOWN:  # Detect right mouse click
        print(f"Right Click at: x={x}, y={y}")
        # Reset
        points.clear()
        if drawing_image is not None:
            drawing_image = current_frame.copy()
            cv2.imshow("Video Frame", drawing_image)

def snap_to_minute(frame_number):
    frames_per_minute = int(fps * 60)
    return round(frame_number / frames_per_minute) * frames_per_minute

def update_frame(*args):
    global drawing_image, current_frame
    frame_number = int(scale.get())
    
    # Snap to nearest minute if enabled
    if snap_enabled.get():
        frame_number = snap_to_minute(frame_number)
        scale.set(frame_number)  # Update slider position to snapped value
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        current_frame = frame.copy()
        drawing_image = frame.copy()
        # Redraw existing points and lines
        for i, point in enumerate(points):
            cv2.circle(drawing_image, point, 5, (0,0,255), -1)
            if i > 0:
                cv2.line(drawing_image, points[i-1], point, (0,255,0), 2)
        cv2.imshow("Video Frame", drawing_image)
        
        # Update time label
        seconds = frame_number / fps
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        time_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")

def toggle_play_pause():
    global is_playing
    is_playing = not is_playing
    play_pause_button.config(text="Pause" if is_playing else "Play")

def video_thread():
    while True:
        if is_playing:
            frame_number = scale.get()
            frame_number = (frame_number + 1) % total_frames
            scale.set(frame_number)
            root.update()
            if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
                break

# Create video scrubber
scale = ttk.Scale(root, from_=0, to=total_frames-1, orient="horizontal", length=400)
scale.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
scale.bind("<Motion>", update_frame)

# Add time label
time_label = ttk.Label(root, text="Time: 00:00")
time_label.grid(row=1, column=0, padx=10, pady=5)

# Add snap checkbox
snap_checkbox = ttk.Checkbutton(root, text="Snap to 1m", variable=snap_enabled)
snap_checkbox.grid(row=1, column=1, padx=10, pady=5)

# Add play/pause button
play_pause_button = ttk.Button(root, text="Play", command=toggle_play_pause)
play_pause_button.grid(row=1, column=2, padx=10, pady=5)

# Create OpenCV window and set mouse callback
cv2.namedWindow("Video Frame")
cv2.setMouseCallback("Video Frame", get_cursor_position)

# Initial frame display
update_frame()

# Start video thread
import threading
threading.Thread(target=video_thread, daemon=True).start()

# Main loop
while True:
    root.update()
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 27:  # ESC key
        print("Clearing points")
        points.clear()
        if drawing_image is not None:
            drawing_image = current_frame.copy()
            cv2.imshow("Video Frame", drawing_image)

# Clean up
cap.release()
cv2.destroyAllWindows()
root.destroy()