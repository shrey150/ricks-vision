import cv2
import numpy as np
from tkinter import Tk, Scale, HORIZONTAL, Label, Entry, Frame, OptionMenu, StringVar, Checkbutton, BooleanVar

# Read the images
image_paths = [
    "../data/line-pics/line-1-marked.png",
    "../data/line-pics/line-2-marked.png",
    "../data/line-pics/line-3-marked.png",
    "../data/line-pics/line-4-marked.png"
]
images = [cv2.imread(path) for path in image_paths]

# Power line coordinates
lines = [
    [(701, 239), (832, 237)],
    [(702, 207), (838, 203)],
    [(695, 185), (868, 180)]
]

def validate_entry(P):
    if P == "": return True
    try:
        float(P)
        return True
    except ValueError:
        return False

def fill_lines(img, lines, thickness, use_blur, blur_size):
    """
    Fill power lines with median pixel value and optionally apply Gaussian blur.
    """
    result = img.copy()
    for pt1, pt2 in lines:
        # Create a mask for the line
        mask = np.zeros_like(result[:, :, 0], dtype=np.uint8)
        cv2.line(mask, pt1, pt2, 255, thickness)

        # Extract pixels under the mask
        masked_pixels = result[mask == 255]

        # Compute median pixel value for the region
        if len(masked_pixels) > 0:
            median_val = tuple(map(int, np.median(masked_pixels, axis=0)))
        else:
            median_val = (0, 0, 0)  # Default to black if no pixels are found

        # Draw the line with the median color
        cv2.line(result, pt1, pt2, median_val, thickness)

    # Apply Gaussian blur if enabled
    if use_blur:
        if blur_size % 2 == 0:
            blur_size += 1  # Ensure kernel size is odd
        result = cv2.GaussianBlur(result, (blur_size, blur_size), 0)

    return result


def update_image(*args):
    """
    Update the displayed image based on user input.
    """
    try:
        alpha = float(alpha_entry.get()) if alpha_entry.get() else alpha_scale.get()
        beta = float(beta_entry.get()) if beta_entry.get() else beta_scale.get()
        gamma = float(gamma_entry.get()) if gamma_entry.get() else gamma_scale.get()
        blur = int(blur_entry.get()) if blur_entry.get() else blur_scale.get()
        if blur % 2 == 0: blur += 1  # Ensure blur is odd
        kernel_size = kernel_scale.get()
        operation = morph_var.get()
        thickness = thickness_scale.get()
        blur_size = blur_scale.get()
        use_fill = fill_var.get()
        use_blur = blur_var.get()
    except ValueError:
        return

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    morph_operations = {
        "Erosion": cv2.erode,
        "Dilation": cv2.dilate,
        "Opening": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_OPEN, k),
        "Closing": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_CLOSE, k),
        "Gradient": lambda img, k: cv2.morphologyEx(img, cv2.MORPH_GRADIENT, k),
    }
    
    processed_images = []
    for i in range(4):
        # Process image
        enhanced_img = cv2.convertScaleAbs(images[i], alpha=alpha / 10.0, beta=beta)
        look_up_table = np.array([((j / 255.0) ** (gamma / 10.0)) * 255 for j in range(256)]).astype("uint8")
        gamma_corrected = cv2.LUT(enhanced_img, look_up_table)
        blurred = cv2.GaussianBlur(gamma_corrected, (blur, blur), 0)
        morphed = morph_operations[operation](blurred, kernel)

        # Apply power line filling if enabled
        if use_fill:
            morphed = fill_lines(morphed, lines, thickness, use_blur, blur_size)

        # Resize all images to same size
        processed_images.append(cv2.resize(morphed, (400, 400)))
    
    # Combine images in 2x2 grid
    top_row = np.hstack([processed_images[0], processed_images[1]])
    bottom_row = np.hstack([processed_images[2], processed_images[3]])
    combined = np.vstack([top_row, bottom_row])
    
    # Show the combined result
    cv2.imshow('All Lines', combined)


# Create Tkinter window
root = Tk()
root.title("Image Enhancement Controls")

# Validation command
vcmd = (root.register(validate_entry), '%P')

# Create frames for existing controls
alpha_frame = Frame(root)
alpha_frame.pack(fill='x', padx=5, pady=5)
Label(alpha_frame, text="Alpha:").pack(side='left')
alpha_scale = Scale(alpha_frame, from_=0, to=1000, orient=HORIZONTAL, length=300)
alpha_scale.set(50)
alpha_scale.pack(side='left')
alpha_entry = Entry(alpha_frame, validate='key', validatecommand=vcmd, width=10)
alpha_entry.pack(side='left', padx=5)

beta_frame = Frame(root)
beta_frame.pack(fill='x', padx=5, pady=5)
Label(beta_frame, text="Beta:").pack(side='left')
beta_scale = Scale(beta_frame, from_=0, to=100, orient=HORIZONTAL, length=300)
beta_scale.set(50)
beta_scale.pack(side='left')
beta_entry = Entry(beta_frame, validate='key', validatecommand=vcmd, width=10)
beta_entry.pack(side='left', padx=5)

gamma_frame = Frame(root)
gamma_frame.pack(fill='x', padx=5, pady=5)
Label(gamma_frame, text="Gamma:").pack(side='left')
gamma_scale = Scale(gamma_frame, from_=0, to=100, orient=HORIZONTAL, length=300)
gamma_scale.set(10)
gamma_scale.pack(side='left')
gamma_entry = Entry(gamma_frame, validate='key', validatecommand=vcmd, width=10)
gamma_entry.pack(side='left', padx=5)

blur_frame = Frame(root)
blur_frame.pack(fill='x', padx=5, pady=5)
Label(blur_frame, text="Blur:").pack(side='left')
blur_scale = Scale(blur_frame, from_=1, to=21, orient=HORIZONTAL, length=300)
blur_scale.set(5)
blur_scale.pack(side='left')
blur_entry = Entry(blur_frame, validate='key', validatecommand=vcmd, width=10)
blur_entry.pack(side='left', padx=5)

morph_frame = Frame(root)
morph_frame.pack(fill='x', padx=5, pady=5)
Label(morph_frame, text="Kernel Size:").pack(side='left')
kernel_scale = Scale(morph_frame, from_=1, to=21, orient=HORIZONTAL, length=300)
kernel_scale.set(3)
kernel_scale.pack(side='left')

operation_frame = Frame(root)
operation_frame.pack(fill='x', padx=5, pady=5)
Label(operation_frame, text="Morphological Operation:").pack(side='left')
morph_var = StringVar(root)
morph_var.set("Erosion")
morph_menu = OptionMenu(operation_frame, morph_var, "Erosion", "Dilation", "Opening", "Closing", "Gradient")
morph_menu.pack(side='left')

# Add new controls for power line processing
line_frame = Frame(root)
line_frame.pack(fill='x', padx=5, pady=5)
Label(line_frame, text="Line Thickness:").pack(side='left')
thickness_scale = Scale(line_frame, from_=1, to=20, orient=HORIZONTAL, length=300)
thickness_scale.set(5)
thickness_scale.pack(side='left')

effect_frame = Frame(root)
effect_frame.pack(fill='x', padx=5, pady=5)
fill_var = BooleanVar(value=True)
fill_checkbox = Checkbutton(effect_frame, text="Enable Median Fill", variable=fill_var, command=update_image)
fill_checkbox.pack(side='left')

blur_var = BooleanVar(value=False)
blur_checkbox = Checkbutton(effect_frame, text="Enable Gaussian Blur", variable=blur_var, command=update_image)
blur_checkbox.pack(side='left')

# Bind scale movement and entry changes to update function
for widget in [alpha_scale, beta_scale, gamma_scale, blur_scale, kernel_scale, thickness_scale]:
    widget.bind("<Motion>", update_image)

alpha_entry.bind("<KeyRelease>", update_image)
beta_entry.bind("<KeyRelease>", update_image)
gamma_entry.bind("<KeyRelease>", update_image)
blur_entry.bind("<KeyRelease>", update_image)

morph_var.trace_add("write", update_image)

# Show initial image
update_image()

# Start Tkinter event loop
root.mainloop()

cv2.destroyAllWindows()
