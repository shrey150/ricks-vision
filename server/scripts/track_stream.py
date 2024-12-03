import cv2
import numpy as np
import os
from tkinter import Tk, Scale, HORIZONTAL, Button, Label, StringVar, OptionMenu, Checkbutton, BooleanVar, Radiobutton
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
root.title("Video Player and Image Enhancer")

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
queue_box = [(535, 498), (481, 493), (828, 155), (857, 152)]  # Coordinates from coords.txt
selected_vertex = None
vertex_radius = 5

# Add this near the other global variables
detection_method = StringVar()
detection_method.set("color")  # Default to color-based method

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

def mouse_callback(event, x, y, flags, param):
    global selected_vertex
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if click is near any vertex
        for i, (vx, vy) in enumerate(queue_box):
            if abs(x - vx) < vertex_radius * 2 and abs(y - vy) < vertex_radius * 2:
                selected_vertex = i
                break
                
    elif event == cv2.EVENT_MOUSEMOVE:
        if selected_vertex is not None:
            queue_box[selected_vertex] = (x, y)
            update_frame()
            
    elif event == cv2.EVENT_LBUTTONUP:
        selected_vertex = None

# Image processing parameters (sliders will update these)
alpha, beta, gamma = 12.7, 42, 10.0
blur, kernel_size = 5, 21
morph_operation = "Opening"
line_thickness = 2
use_fill, use_blur = True, False
draw_lines = BooleanVar()
draw_lines.set(True)

# Morphological operations dictionary
morph_operations = {
    "Erosion": cv2.erode,
    "Dilation": cv2.dilate,
    "Opening": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_OPEN, k),
    "Closing": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_CLOSE, k),
    "Gradient": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_GRADIENT, k),
}

def set_param(param_name, value):
    """Update global parameters based on slider inputs and refresh the frame."""
    global alpha, beta, gamma, blur, kernel_size, morph_operation, draw_lines
    if param_name == "alpha":
        alpha = float(value)
    elif param_name == "beta":
        beta = float(value)
    elif param_name == "gamma":
        gamma = float(value)
    elif param_name == "blur":
        blur = int(value)
        if blur % 2 == 0:
            blur += 1  # Ensure blur size is odd
    elif param_name == "kernel_size":
        kernel_size = int(value)
        if kernel_size % 2 == 0:
            kernel_size += 1  # Ensure kernel size is odd
    elif param_name == "morph_operation":
        morph_operation = value
    elif param_name == "draw_lines":
        draw_lines = value

    # Redraw the frame with updated parameters
    update_frame()

def detect_line_fill_percentage(frame, polygon, dark_thresh=50, cluster_thresh=5, angle_tolerance=15):
    """
    Estimates the queue fill percentage using either color-based or darkness-based detection.
    """
    # Method 1: Color-based detection
    def detect_non_white_regions(image, queue_box, kernel_size=15):
        mask = np.zeros_like(image[:, :, 0])
        cv2.fillPoly(mask, [np.array(queue_box, dtype=np.int32)], 255)
        
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        non_white_mask = cv2.inRange(masked_image, (0, 0, 0), (200, 200, 200))
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        morphed = cv2.morphologyEx(non_white_mask, cv2.MORPH_CLOSE, kernel)
        
        queue_start = min(queue_box, key=lambda p: p[1])
        queue_end = max(queue_box, key=lambda p: p[1])
        queue_height = queue_end[1] - queue_start[1]
        
        ys, xs = np.where(morphed > 0)
        y_values_in_box = ys[(xs >= queue_start[0]) & (xs <= queue_end[0])]
        
        if len(y_values_in_box) == 0:
            return 0.0, queue_end[1]
            
        end_y = np.max(y_values_in_box)
        filled_height = end_y - queue_start[1]
        filled_percentage = (filled_height / queue_height) * 100
        
        # Visualization
        cv2.line(frame, (queue_start[0], queue_start[1]), 
                (queue_start[0], int(end_y)), (0, 255, 0), 2)
        
        return min(filled_percentage, 100.0), end_y

    # Method 2: Darkness-based detection
    def detect_darkness(frame, polygon, dark_thresh):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(gray)
        cv2.fillPoly(mask, [np.array(polygon, dtype=np.int32)], 255)

        points = np.array(polygon)
        queue_start = points[points[:, 1].argmax()]
        queue_end = points[points[:, 1].argmin()]
        queue_length = np.linalg.norm(queue_end - queue_start)

        dark_pixels = (gray < dark_thresh) & (mask == 255)
        
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            dark_pixels.astype(np.uint8), connectivity=8
        )

        if num_labels <= 1:
            return 0.0

        dark_coords = np.column_stack(np.where(dark_pixels))[:, ::-1]
        queue_vector = queue_end - queue_start
        queue_unit = queue_vector / queue_length

        projections = np.dot(dark_coords - queue_start, queue_unit)
        min_proj = np.min(projections[projections >= 0])
        max_proj = np.min([np.max(projections), queue_length])

        filled_length = max_proj - min_proj
        return (filled_length / queue_length) * 100

    # Choose method based on radio button selection
    if detection_method.get() == "color":
        percentage, _ = detect_non_white_regions(frame, polygon)
    else:  # darkness
        percentage = detect_darkness(frame, polygon, dark_thresh)

    return min(percentage, 100.0)



def process_image(image, alpha, beta, gamma, blur, kernel_size, morph_operation, lines, line_thickness, use_fill, use_blur, draw_lines):
    """Image enhancement pipeline."""
    enhanced_img = cv2.convertScaleAbs(image, alpha=alpha / 10.0, beta=beta)
    look_up_table = np.array([((i / 255.0) ** (gamma / 10.0)) * 255 for i in range(256)]).astype("uint8")
    gamma_corrected = cv2.LUT(enhanced_img, look_up_table)
    blurred = cv2.GaussianBlur(gamma_corrected, (blur, blur), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    morphed = morph_operations[morph_operation](blurred, kernel)

    if use_fill:
        morphed = fill_lines(morphed, lines, line_thickness, use_blur, blur)

    if draw_lines:
        for line in lines:
            cv2.line(morphed, line[0], line[1], (0, 0, 255), line_thickness)

    return morphed


def fill_lines(img, lines, thickness, use_blur, blur_size):
    """Fill power lines with median pixel value and optionally apply Gaussian blur."""
    result = img.copy()
    for pt1, pt2 in lines:
        mask = np.zeros_like(result[:, :, 0], dtype=np.uint8)
        cv2.line(mask, pt1, pt2, 255, thickness)
        masked_pixels = result[mask == 255]
        median_val = tuple(map(int, np.median(masked_pixels, axis=0))) if len(masked_pixels) > 0 else (0, 0, 0)
        cv2.line(result, pt1, pt2, median_val, thickness)

    if use_blur:
        blur_size = blur_size if blur_size % 2 != 0 else blur_size + 1
        result = cv2.GaussianBlur(result, (blur_size, blur_size), 0)

    return result


def process_frame(frame_number):
    """Process a single frame."""
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        return None
    
        height, width, _ = frame.shape
    
    # Commented out YOLO detection for faster scrubbing
    '''
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
    '''
    count_in_queue = 0  # Placeholder while detection is disabled

    # Enhance image
    lines = [[(701, 239), (832, 237)], [(702, 207), (838, 203)], [(695, 185), (868, 180)]]
    frame = process_image(frame, alpha, beta, gamma, blur, kernel_size, morph_operation, lines, line_thickness, use_fill, use_blur, draw_lines)

    # Draw queue region as a polygon
    points = np.array(queue_box, np.int32).reshape((-1, 1, 2))
    cv2.polylines(frame, [points], True, (255, 0, 0), 2)

    # Draw draggable vertices
    for x, y in queue_box:
        cv2.circle(frame, (x, y), vertex_radius, (0, 0, 255), -1)

    # Detect line fill percentage
    line_fill_percentage = detect_line_fill_percentage(frame, queue_box)

    # Update frame
    return frame, 0, line_fill_percentage

def update_frame():
    """Update the frame."""
    frame_number = scale.get()
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, original_frame = cap.read()
    if ret:
        # Process the frame
        processed_result = process_frame(frame_number)
        if processed_result:
            processed_frame, people_count, line_length = processed_result
            
            # Show original frame
            cv2.imshow("Original Frame", original_frame)
            
            # Show processed frame
            cv2.imshow("Processed Frame", processed_frame)
            
            # Update information label
            info_label.config(text=f"People: {people_count}, Line Length: {line_length}")


def toggle_play_pause():
    """Toggle play/pause state."""
    global is_playing
    is_playing = not is_playing
    play_pause_button.config(text="Pause" if is_playing else "Play")

def video_thread():
    """Thread for playing the video."""
    while True:
        if is_playing:
            frame_number = scale.get()
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, original_frame = cap.read()
            if ret:
                processed_result = process_frame(frame_number)
                if processed_result:
                    processed_frame, people_count, line_length = processed_result

                    # Show original frame
                    cv2.imshow("Original Frame", original_frame)

                    # Show processed frame
                    cv2.imshow("Processed Frame", processed_frame)

                    # Update scale and wait for next frame
                    cv2.waitKey(int(1000 / fps))
                    scale.set((frame_number + 1) % total_frames)


# Tkinter controls for image processing
Label(root, text="Alpha").grid(row=2, column=0)
alpha_slider = Scale(root, from_=1, to=100, orient=HORIZONTAL, command=lambda v: set_param("alpha", v))
alpha_slider.set(alpha)
alpha_slider.grid(row=2, column=1)

Label(root, text="Beta").grid(row=3, column=0)
beta_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=lambda v: set_param("beta", v))
beta_slider.set(beta)
beta_slider.grid(row=3, column=1)

Label(root, text="Gamma").grid(row=4, column=0)
gamma_slider = Scale(root, from_=1, to=100, orient=HORIZONTAL, command=lambda v: set_param("gamma", v))
gamma_slider.set(gamma)
gamma_slider.grid(row=4, column=1)

Label(root, text="Blur").grid(row=5, column=0)
blur_slider = Scale(root, from_=1, to=21, orient=HORIZONTAL, command=lambda v: set_param("blur", v))
blur_slider.set(blur)
blur_slider.grid(row=5, column=1)

Label(root, text="Kernel Size").grid(row=6, column=0)
kernel_slider = Scale(root, from_=1, to=21, orient=HORIZONTAL, command=lambda v: set_param("kernel_size", v))
kernel_slider.set(kernel_size)
kernel_slider.grid(row=6, column=1)

morph_var = StringVar(root)
morph_var.set("Opening")
morph_menu = OptionMenu(root, morph_var, *morph_operations.keys(), command=lambda v: set_param("morph_operation", v))
morph_menu.grid(row=7, column=1)

draw_lines_checkbox = Checkbutton(root, text="Draw Power Lines", variable=draw_lines, command=lambda: set_param("draw_lines", draw_lines.get()))
draw_lines_checkbox.grid(row=8, column=0, padx=10, pady=10)

# Add these radio buttons near the other Tkinter controls
Label(root, text="Detection Method:").grid(row=10, column=0)
Radiobutton(root, text="Color-based", variable=detection_method, value="color", 
            command=lambda: update_frame()).grid(row=10, column=1, sticky="w")
Radiobutton(root, text="Darkness-based", variable=detection_method, value="darkness", 
            command=lambda: update_frame()).grid(row=11, column=1, sticky="w")

# Play/pause button
play_pause_button = Button(root, text="Play", command=toggle_play_pause)
play_pause_button.grid(row=9, column=0, padx=10, pady=10)

# Start video thread
threading.Thread(target=video_thread, daemon=True).start()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
