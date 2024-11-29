import cv2
import numpy as np
from tkinter import Tk, Scale, HORIZONTAL, Label, Entry, Frame, Button, IntVar, OptionMenu, StringVar

# Read the images
image_paths = [
    "../data/line-pics/line-1-marked.png",
    "../data/line-pics/line-2-marked.png", 
    "../data/line-pics/line-3-marked.png",
    "../data/line-pics/line-4-marked.png"
]
images = [cv2.imread(path) for path in image_paths]
reference_image = None  # For background subtraction

def save_reference_image():
    """Save the first image as a reference for background subtraction."""
    global reference_image
    reference_image = cv2.cvtColor(images[0], cv2.COLOR_BGR2GRAY)
    print("Reference image saved for background subtraction.")

def validate_entry(P):
    if P == "": return True
    try:
        float(P)
        return True
    except ValueError:
        return False

def reset_effects():
    """Reset all sliders and controls to their default values."""
    alpha_scale.set(10)  # Reset alpha to no effect
    beta_scale.set(0)    # Reset beta to no effect
    gamma_scale.set(10)  # Reset gamma to no effect
    blur_scale.set(1)    # Reset blur to no effect
    kernel_scale.set(3)  # Default kernel size
    edge_thresh1_scale.set(100)  # Default Canny threshold 1
    edge_thresh2_scale.set(200)  # Default Canny threshold 2
    threshold_scale.set(127)     # Default threshold value
    morph_var.set("Erosion")     # Default morphological operation
    bg_subtract.set(0)           # Disable background subtraction
    update_image()

def update_image(*args):
    try:
        alpha = float(alpha_entry.get()) if alpha_entry.get() else alpha_scale.get()
        beta = float(beta_entry.get()) if beta_entry.get() else beta_scale.get()
        gamma = float(gamma_entry.get()) if gamma_entry.get() else gamma_scale.get()
        blur = int(blur_entry.get()) if blur_entry.get() else blur_scale.get()
        if blur % 2 == 0: blur += 1  # Ensure blur is odd
        kernel_size = kernel_scale.get()
        morph_operation = morph_var.get()
        edge_thresh1 = edge_thresh1_scale.get()
        edge_thresh2 = edge_thresh2_scale.get()
        threshold_value = threshold_scale.get()
        background_subtract = bg_subtract.get()
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
    for img in images:
        # Grayscale conversion
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Enhancement (alpha, beta, gamma)
        enhanced_img = cv2.convertScaleAbs(img, alpha=alpha / 10.0, beta=beta)
        look_up_table = np.array([((i / 255.0) ** (gamma / 10.0)) * 255 for i in range(256)]).astype("uint8")
        gamma_corrected = cv2.LUT(enhanced_img, look_up_table)
        
        # Blur
        blurred = cv2.GaussianBlur(gamma_corrected, (blur, blur), 0)
        
        # Morphological Transformation
        morphed = morph_operations[morph_operation](blurred, kernel)
        
        # Edge Detection
        edges = cv2.Canny(gray, edge_thresh1, edge_thresh2)
        
        # Thresholding
        _, thresholded = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        
        # Background Subtraction
        if background_subtract and reference_image is not None:
            fg_mask = cv2.absdiff(gray, reference_image)
            _, fg_mask = cv2.threshold(fg_mask, threshold_value, 255, cv2.THRESH_BINARY)
        else:
            fg_mask = gray  # No subtraction applied
        
        # Combine results (threshold, edges, background subtraction)
        combined = cv2.merge([thresholded, edges, fg_mask])
        processed_images.append(cv2.resize(combined, (400, 400)))
    
    # Combine images in 2x2 grid
    top_row = np.hstack([processed_images[0], processed_images[1]])
    bottom_row = np.hstack([processed_images[2], processed_images[3]])
    final_result = np.vstack([top_row, bottom_row])
    
    # Show the combined result
    cv2.imshow('Processed Images', final_result)

# Create Tkinter window
root = Tk()
root.title("Image Processing Controls")

# Validation command
vcmd = (root.register(validate_entry), '%P')

# Contrast/Brightness Controls
alpha_frame = Frame(root)
alpha_frame.pack(fill='x', padx=5, pady=5)
Label(alpha_frame, text="Alpha:").pack(side='left')
alpha_scale = Scale(alpha_frame, from_=0, to=1000, orient=HORIZONTAL, length=300)
alpha_scale.set(10)
alpha_scale.pack(side='left')
alpha_entry = Entry(alpha_frame, validate='key', validatecommand=vcmd, width=10)
alpha_entry.pack(side='left', padx=5)

beta_frame = Frame(root)
beta_frame.pack(fill='x', padx=5, pady=5)
Label(beta_frame, text="Beta:").pack(side='left')
beta_scale = Scale(beta_frame, from_=0, to=100, orient=HORIZONTAL, length=300)
beta_scale.set(0)
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
blur_scale.set(1)
blur_scale.pack(side='left')
blur_entry = Entry(blur_frame, validate='key', validatecommand=vcmd, width=10)
blur_entry.pack(side='left', padx=5)

# Morphological Transformation Controls
morph_frame = Frame(root)
morph_frame.pack(fill='x', padx=5, pady=5)
Label(morph_frame, text="Kernel Size:").pack(side='left')
kernel_scale = Scale(morph_frame, from_=1, to=21, orient=HORIZONTAL, length=300)
kernel_scale.set(3)
kernel_scale.pack(side='left')
Label(morph_frame, text="Morphological Operation:").pack(side='left')
morph_var = StringVar(root)
morph_var.set("Erosion")
morph_menu = OptionMenu(morph_frame, morph_var, "Erosion", "Dilation", "Opening", "Closing", "Gradient")
morph_menu.pack(side='left')

# Edge Detection Controls
edge_frame = Frame(root)
edge_frame.pack(fill='x', padx=5, pady=5)
Label(edge_frame, text="Canny Edge Thresh1:").pack(side='left')
edge_thresh1_scale = Scale(edge_frame, from_=0, to=255, orient=HORIZONTAL, length=300)
edge_thresh1_scale.set(100)
edge_thresh1_scale.pack(side='left')
Label(edge_frame, text="Canny Edge Thresh2:").pack(side='left')
edge_thresh2_scale = Scale(edge_frame, from_=0, to=255, orient=HORIZONTAL, length=300)
edge_thresh2_scale.set(200)
edge_thresh2_scale.pack(side='left')

# Thresholding Controls
threshold_frame = Frame(root)
threshold_frame.pack(fill='x', padx=5, pady=5)
Label(threshold_frame, text="Threshold Value:").pack(side='left')
threshold_scale = Scale(threshold_frame, from_=0, to=255, orient=HORIZONTAL, length=300)
threshold_scale.set(127)
threshold_scale.pack(side='left')

# Background Subtraction Controls
bg_frame = Frame(root)
bg_frame.pack(fill='x', padx=5, pady=5)
Label(bg_frame, text="Background Subtraction:").pack(side='left')
bg_subtract = IntVar()
Button(bg_frame, text="Save Reference Image", command=save_reference_image).pack(side='left')

# Reset Effects Button
reset_frame = Frame(root)
reset_frame.pack(fill='x', padx=5, pady=5)
Button(reset_frame, text="Reset Effects", command=reset_effects).pack(side='left')

# Bind sliders and controls to the update function
alpha_scale.bind("<Motion>", update_image)
beta_scale.bind("<Motion>", update_image)
gamma_scale.bind("<Motion>", update_image)
blur_scale.bind("<Motion>", update_image)
kernel_scale.bind("<Motion>", update_image)
morph_var.trace_add("write", update_image)
edge_thresh1_scale.bind("<Motion>", update_image)
edge_thresh2_scale.bind("<Motion>", update_image)
threshold_scale.bind("<Motion>", update_image)

alpha_entry.bind("<KeyRelease>", update_image)
beta_entry.bind("<KeyRelease>", update_image)
gamma_entry.bind("<KeyRelease>", update_image)
blur_entry.bind("<KeyRelease>", update_image)

# Show initial image
update_image()

# Start Tkinter loop
root.mainloop()

cv2.destroyAllWindows()
