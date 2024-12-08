import cv2
import numpy as np
import os
from tkinter import Tk, Scale, HORIZONTAL, Button, Label, StringVar, OptionMenu, Checkbutton, BooleanVar, Radiobutton
import threading

# Load YOLO (Optional - currently not used)
net = cv2.dnn.readNet(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3", "yolov3.weights"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "models", "yolov3", "yolov3.cfg")
)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Video path
video_path = "../data/ricks-stream.ts"
cap = cv2.VideoCapture(video_path)

root = Tk()
root.title("Video Player and Image Enhancer")

# Video properties
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

scale = Scale(root, from_=0, to=total_frames - 1, orient=HORIZONTAL, length=500)
scale.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

info_label = Label(root, text="People: 0, Line Length: 0%")
info_label.grid(row=1, column=0, padx=10, pady=10)

is_playing = False

# Define your queue polygon
queue_box = [(535, 498), (481, 493), (828, 155), (857, 152)]
selected_vertex = None
vertex_radius = 5

detection_method = StringVar()
detection_method.set("color")

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
                        xinters = (y - p1y)*(p2x - p1x)/(p2y - p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def mouse_callback(event, x, y, flags, param):
    global selected_vertex
    if event == cv2.EVENT_LBUTTONDOWN:
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

# "Deep fry" defaults
alpha = 100
beta = 37
gamma = 83
blur = 5
kernel_size = 21
morph_operation = "Opening"
line_thickness = 2
use_fill, use_blur = True, False
draw_lines = BooleanVar()
draw_lines.set(False)

morph_operations = {
    "Erosion": cv2.erode,
    "Dilation": cv2.dilate,
    "Opening": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_OPEN, k),
    "Closing": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_CLOSE, k),
    "Gradient": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_GRADIENT, k),
}

def set_param(param_name, value):
    global alpha, beta, gamma, blur, kernel_size, morph_operation, draw_lines
    if param_name == "alpha":
        alpha = float(value)
    elif param_name == "beta":
        beta = float(value)
    elif param_name == "gamma":
        gamma = float(value)
    elif param_name == "blur":
        b = int(value)
        blur = b if b % 2 == 1 else b + 1
    elif param_name == "kernel_size":
        k = int(value)
        kernel_size = k if k % 2 == 1 else k + 1
    elif param_name == "morph_operation":
        morph_operation = value
    elif param_name == "draw_lines":
        draw_lines = value
    update_frame()

def detect_line_fill_percentage(frame, polygon, dark_thresh=50):
    if detection_method.get() == "color":
        percentage, filled_dist, morphed = detect_non_white_regions(frame, polygon)
    else:
        percentage = detect_darkness(frame, polygon, dark_thresh)
        morphed = None
        filled_dist = None
    return min(percentage, 100.0), morphed, filled_dist

def detect_non_white_regions(image, queue_box, kernel_size_close=15):
    # Create mask for polygon
    mask = np.zeros_like(image[:, :, 0])
    cv2.fillPoly(mask, [np.array(queue_box, dtype=np.int32)], 255)
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    # Threshold non-white pixels
    non_white_mask = cv2.inRange(masked_image, (0, 0, 0), (200, 200, 200))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size_close, kernel_size_close))
    morphed = cv2.morphologyEx(non_white_mask, cv2.MORPH_CLOSE, kernel)

    ys, xs = np.where(morphed > 0)
    if len(xs) == 0:
        return 0.0, None, morphed

    queue_start = np.array(queue_box[0], dtype=float)
    queue_end = np.array(queue_box[-1], dtype=float)
    queue_vector = queue_end - queue_start
    queue_length = np.linalg.norm(queue_vector)
    if queue_length == 0:
        return 0.0, None, morphed

    queue_unit = queue_vector / queue_length
    pixel_coords = np.column_stack((xs, ys))
    projections = np.dot(pixel_coords - queue_start, queue_unit)
    valid_projections = projections[(projections >= 0) & (projections <= queue_length)]

    if len(valid_projections) == 0:
        return 0.0, None, morphed

    filled_distance = np.max(valid_projections)
    filled_percentage = (filled_distance / queue_length) * 100.0
    return filled_percentage, filled_distance, morphed

def detect_darkness(frame, polygon, dark_thresh):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(gray)
    cv2.fillPoly(mask, [np.array(polygon, dtype=np.int32)], 255)

    queue_start = np.array(polygon[0], dtype=float)
    queue_end = np.array(polygon[-1], dtype=float)
    queue_vector = queue_end - queue_start
    queue_length = np.linalg.norm(queue_vector)
    if queue_length == 0:
        return 0.0
    queue_unit = queue_vector / queue_length

    dark_pixels = (gray < dark_thresh) & (mask == 255)
    dark_coords = np.column_stack(np.where(dark_pixels))[:, ::-1]
    if len(dark_coords) == 0:
        return 0.0

    projections = np.dot(dark_coords - queue_start, queue_unit)
    valid_projections = projections[(projections >= 0) & (projections <= queue_length)]
    if len(valid_projections) == 0:
        return 0.0
    filled_distance = np.max(valid_projections)
    return (filled_distance / queue_length) * 100.0

def process_image(image, alpha, beta, gamma_val, blur_size, kernel_size_val, morph_operation, lines, line_thickness, use_fill, use_blur, draw_lines):
    alpha_scaled = alpha / 10.0
    gamma_scaled = gamma_val / 10.0
    enhanced_img = cv2.convertScaleAbs(image, alpha=alpha_scaled, beta=beta)
    look_up_table = np.array([((i / 255.0) ** gamma_scaled) * 255 for i in range(256)]).astype("uint8")
    gamma_corrected = cv2.LUT(enhanced_img, look_up_table)
    blurred = cv2.GaussianBlur(gamma_corrected, (blur_size, blur_size), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size_val, kernel_size_val))
    morphed = morph_operations[morph_operation](blurred, kernel)

    if use_fill:
        morphed = fill_lines(morphed, lines, line_thickness, use_blur, blur_size)

    if draw_lines:
        for line in lines:
            cv2.line(morphed, line[0], line[1], (0, 0, 255), line_thickness)

    return morphed

def fill_lines(img, lines, thickness, use_blur, blur_size):
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
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        return None

    count_in_queue = 0
    lines = [[(701, 239), (832, 237)], [(702, 207), (838, 203)], [(695, 185), (868, 180)]]
    processed = process_image(frame, alpha, beta, gamma, blur, kernel_size, morph_operation, lines, line_thickness, use_fill, use_blur, draw_lines)

    # Draw queue polygon and vertices
    points = np.array(queue_box, np.int32).reshape((-1, 1, 2))
    cv2.polylines(processed, [points], True, (255, 0, 0), 2)
    for x, y in queue_box:
        cv2.circle(processed, (x, y), vertex_radius, (0, 0, 255), -1)

    line_fill_percentage, morphed_mask, filled_distance = detect_line_fill_percentage(processed, queue_box)

    return frame, processed, count_in_queue, line_fill_percentage, morphed_mask, filled_distance

def update_frame(*args):
    frame_number = scale.get()
    result = process_frame(frame_number)
    if result:
        original_frame, processed_frame, people_count, line_length, morphed_mask, filled_distance = result
        cv2.imshow("Original Frame", original_frame)
        cv2.imshow("Processed Frame", processed_frame)

        # Visualization of the queue box intermediate step
        if detection_method.get() == "color" and morphed_mask is not None:
            # Invert the mask so black = filled, white = empty
            queue_box_visual = 255 - morphed_mask
            queue_box_visual = cv2.cvtColor(queue_box_visual, cv2.COLOR_GRAY2BGR)

            # Draw line to indicate the projection (for reference only)
            queue_start = np.array(queue_box[0], dtype=float)
            queue_end = np.array(queue_box[-1], dtype=float)
            queue_vector = queue_end - queue_start
            queue_length = np.linalg.norm(queue_vector)
            if queue_length > 0 and filled_distance is not None:
                queue_unit = queue_vector / queue_length
                proj_end = (queue_start + queue_unit * filled_distance).astype(int)
                cv2.line(queue_box_visual, tuple(queue_start.astype(int)), tuple(proj_end), (0, 0, 255), 2)
                cv2.circle(queue_box_visual, tuple(proj_end), 5, (0,0,255), -1)

            # Calculate the fullness based on black/white ratio inside polygon
            # Convert visualization to grayscale to count black/white pixels easily
            gray_visual = cv2.cvtColor(queue_box_visual, cv2.COLOR_BGR2GRAY)

            # Create polygon mask again
            poly_mask = np.zeros_like(gray_visual)
            cv2.fillPoly(poly_mask, [np.array(queue_box, dtype=np.int32)], 255)

            # Count pixels inside polygon
            inside_polygon = poly_mask == 255
            total_pixels = np.count_nonzero(inside_polygon)
            # Black pixels are where gray_visual == 0
            black_pixels = np.count_nonzero((gray_visual == 0) & inside_polygon)
            
            # Compute fullness percentage
            if total_pixels > 0:
                fullness_percentage = (black_pixels / total_pixels) * 100.0
            else:
                fullness_percentage = 0.0

            # Show updated fullness percentage in the UI
            info_label.config(text=f"People: {people_count}, Line Fullness: {fullness_percentage:.2f}%")

            cv2.imshow("Queue Box Visualization", queue_box_visual)

        else:
            # Darkness-based or no mask scenario
            blank_visual = np.full((original_frame.shape[0], original_frame.shape[1], 3), 255, dtype=np.uint8)
            cv2.fillPoly(blank_visual, [np.array(queue_box, dtype=np.int32)], (200, 200, 200))
            cv2.putText(blank_visual, "No intermediate mask (Darkness-based)", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
            cv2.imshow("Queue Box Visualization", blank_visual)
            
            # For darkness-based method, if you want a similar fullness measure:
            # You could replicate a similar process by creating a binary mask for dark pixels and inverting it.
            # Otherwise, just show the previously computed line_length or 100% placeholder.
            info_label.config(text=f"People: {people_count}, Line Length: {line_length:.4f}%")

def toggle_play_pause():
    global is_playing
    is_playing = not is_playing
    play_pause_button.config(text="Pause" if is_playing else "Play")

def video_thread():
    while True:
        if is_playing:
            frame_number = scale.get()
            frame_number = (frame_number + 1) % total_frames
            result = process_frame(frame_number)
            if result:
                original_frame, processed_frame, people_count, line_length, morphed_mask, filled_distance = result
                cv2.imshow("Original Frame", original_frame)
                cv2.imshow("Processed Frame", processed_frame)

                # Update Queue Box Visualization
                if detection_method.get() == "color" and morphed_mask is not None:
                    queue_box_visual = 255 - morphed_mask
                    queue_box_visual = cv2.cvtColor(queue_box_visual, cv2.COLOR_GRAY2BGR)

                    queue_start = np.array(queue_box[0], dtype=float)
                    queue_end = np.array(queue_box[-1], dtype=float)
                    queue_vector = queue_end - queue_start
                    queue_length = np.linalg.norm(queue_vector)
                    if queue_length > 0 and filled_distance is not None:
                        queue_unit = queue_vector / queue_length
                        proj_end = (queue_start + queue_unit * filled_distance).astype(int)
                        cv2.line(queue_box_visual, tuple(queue_start.astype(int)), tuple(proj_end), (0, 0, 255), 2)
                        cv2.circle(queue_box_visual, tuple(proj_end), 5, (0,0,255), -1)
                    cv2.imshow("Queue Box Visualization", queue_box_visual)
                else:
                    blank_visual = np.full((original_frame.shape[0], original_frame.shape[1], 3), 255, dtype=np.uint8)
                    cv2.fillPoly(blank_visual, [np.array(queue_box, dtype=np.int32)], (200, 200, 200))
                    cv2.putText(blank_visual, "No intermediate mask (Darkness-based)", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
                    cv2.imshow("Queue Box Visualization", blank_visual)

                info_label.config(text=f"People: {people_count}, Line Length: {line_length:.4f}%")
                cv2.waitKey(int(1000 / fps))
                scale.set(frame_number)

# Bind scale movement
scale.bind("<Motion>", lambda event: update_frame())

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

Label(root, text="Detection Method:").grid(row=10, column=0)
Radiobutton(root, text="Color-based", variable=detection_method, value="color", command=lambda: update_frame()).grid(row=10, column=1, sticky="w")
Radiobutton(root, text="Darkness-based", variable=detection_method, value="darkness", command=lambda: update_frame()).grid(row=11, column=1, sticky="w")

play_pause_button = Button(root, text="Play", command=toggle_play_pause)
play_pause_button.grid(row=9, column=0, padx=10, pady=10)

threading.Thread(target=video_thread, daemon=True).start()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
