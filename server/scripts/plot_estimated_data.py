import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_non_white_regions(image, queue_box, kernel_size_close=15):
    # Create mask for polygon
    mask = np.zeros_like(image[:, :, 0])
    cv2.fillPoly(mask, [np.array(queue_box, dtype=np.int32)], 255)
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    # Threshold non-white pixels
    non_white_mask = cv2.inRange(masked_image, (0, 0, 0), (200, 200, 200))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size_close, kernel_size_close))
    morphed = cv2.morphologyEx(non_white_mask, cv2.MORPH_CLOSE, kernel)

    # Calculate fullness percentage
    poly_mask = np.zeros_like(morphed)
    cv2.fillPoly(poly_mask, [np.array(queue_box, dtype=np.int32)], 255)
    
    # Count pixels inside polygon
    inside_polygon = poly_mask == 255
    total_pixels = np.count_nonzero(inside_polygon)
    # Black pixels in morphed mask are where morphed > 0
    filled_pixels = np.count_nonzero((morphed > 0) & inside_polygon)
    
    # Compute fullness percentage
    if total_pixels > 0:
        fullness_percentage = (filled_pixels / total_pixels) * 100.0
    else:
        fullness_percentage = 0.0
        
    return fullness_percentage

def process_image(image):
    # Apply basic image enhancement
    alpha_scaled = 10.0  # alpha/10.0
    beta = 37
    enhanced_img = cv2.convertScaleAbs(image, alpha=alpha_scaled, beta=beta)
    
    # Apply basic blur
    blur_size = 5
    blurred = cv2.GaussianBlur(enhanced_img, (blur_size, blur_size), 0)
    
    # Apply morphological operation
    kernel_size = 21
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    processed = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)
    
    return processed

def main():
    # Video path
    video_path = "../data/ricks-stream.ts"  # Adjust path as needed
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Queue box coordinates from original script
    queue_box = [(535, 498), (481, 493), (828, 155), (857, 152)]
    
    # Store results
    minutes = []
    fullness_values = []
    
    # Process one frame per minute
    frames_per_minute = int(fps * 60)
    
    for minute in range(31):  # 0 to 30 minutes
        frame_number = minute * frames_per_minute
        
        if frame_number >= total_frames:
            break
            
        # Skip minutes 27 and 28 as specified
        if minute in [27, 28]:
            continue
            
        # Read and process frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if not ret:
            print(f"Error reading frame at minute {minute}")
            continue
            
        processed_frame = process_image(frame)
        fullness = detect_non_white_regions(processed_frame, queue_box)
        
        minutes.append(minute)
        fullness_values.append(fullness)
        
        print(f"Minute {minute}: {fullness:.2f}%")
    
    cap.release()
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(minutes, fullness_values, 'b-o', linewidth=2, markersize=6)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Customize the plot
    plt.title('Rick\'s Line Length Over Time (Estimated)', fontsize=14, pad=15)
    plt.xlabel('Time (minutes)', fontsize=12)
    plt.ylabel('Fullness Percentage (%)', fontsize=12)
    
    # Set y-axis limits from 0 to 100%
    plt.ylim(0, 100)
    
    # Add minor gridlines
    plt.grid(True, which='minor', linestyle=':', alpha=0.4)
    plt.minorticks_on()
    
    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()