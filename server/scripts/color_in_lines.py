import cv2
import numpy as np
import tkinter as tk

# Function to apply Gaussian Blur to a line's region
def apply_gaussian_blur(image, start, end, thickness):
    # Define the bounding box for the line
    x_min, y_min = min(start[0], end[0]), min(start[1], end[1])
    x_max, y_max = max(start[0], end[0]), max(start[1], end[1])
    
    # Expand the region slightly around the line for the blur effect
    padding = thickness * 2
    x_min, x_max = max(0, x_min - padding), min(image.shape[1], x_max + padding)
    y_min, y_max = max(0, y_min - padding), min(image.shape[0], y_max + padding)
    
    # Extract the region and apply Gaussian Blur
    region = image[y_min:y_max, x_min:x_max]
    blurred_region = cv2.GaussianBlur(region, (15, 15), 0)
    
    # Replace the region in the image with the blurred version
    image[y_min:y_max, x_min:x_max] = blurred_region

# Function to apply either median coloring or Gaussian Blur
def apply_effect(image, apply_lines, use_blur):
    # Coordinates for the lines
    lines = [
        ((701, 239), (832, 237)),  # Line 1
        ((702, 207), (838, 203)),  # Line 2
        ((695, 185), (868, 180))   # Line 3
    ]
    # Line thickness
    thickness = 10

    for start, end in lines:
        if use_blur:
            # Apply Gaussian Blur around the line
            apply_gaussian_blur(image, start, end, thickness)
        elif apply_lines:
            # Compute the bounding box and median fill
            x_min, y_min = min(start[0], end[0]), min(start[1], end[1])
            x_max, y_max = max(start[0], end[0]), max(start[1], end[1])
            x_min, x_max = max(0, x_min), min(image.shape[1] - 1, x_max)
            y_min, y_max = max(0, y_min), min(image.shape[0] - 1, y_max)
            region = image[y_min:y_max+1, x_min:x_max+1]
            median_color = np.median(region.reshape(-1, 3), axis=0)
            median_color = tuple(map(int, median_color))
            cv2.line(image, start, end, median_color, thickness)
    return image

# Function to update the image when a control is toggled
def update_image():
    global processed_image
    processed_image = image.copy()
    processed_image = apply_effect(processed_image, var_apply_lines.get(), var_use_blur.get())
    img_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
    img_tk = cv2.imencode('.ppm', img_rgb)[1].tobytes()
    canvas_image.configure(data=img_tk)

# Load the image
image_path = "../data/ricks-frame.jpg"
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Image not found: {image_path}")
processed_image = image.copy()

# Create the Tkinter window
root = tk.Tk()
root.title("Power Line Processing")

# Checkbox for applying line effects
var_apply_lines = tk.BooleanVar()
var_apply_lines.set(True)
checkbox_lines = tk.Checkbutton(root, text="Apply Median Fill", variable=var_apply_lines, command=update_image)
checkbox_lines.pack()

# Checkbox for Gaussian Blur
var_use_blur = tk.BooleanVar()
var_use_blur.set(False)
checkbox_blur = tk.Checkbutton(root, text="Apply Gaussian Blur", variable=var_use_blur, command=update_image)
checkbox_blur.pack()

# Canvas to display the image
canvas = tk.Label(root)
canvas.pack()

img_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
img_tk = cv2.imencode('.ppm', img_rgb)[1].tobytes()
canvas_image = tk.Label(root, image=None)
canvas_image.pack()
canvas_image.configure(data=img_tk)

# Start Tkinter loop
root.mainloop()
