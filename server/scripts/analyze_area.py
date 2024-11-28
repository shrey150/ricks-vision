import cv2
import numpy as np

def analyze_filled_area_fixed(image, queue_box):
    # Convert the list of coordinates to a NumPy array
    polygon = np.array(queue_box, dtype=np.int32)

    # Step 1: Create a stricter mask for the polygon
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    masked_image = cv2.bitwise_and(image, image, mask=mask)

    # Step 2: Convert masked area to grayscale
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

    # Step 3: Apply adaptive thresholding for better contrast handling
    thresholded = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Step 4: Apply morphological operations to clean up noise
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)

    # Step 5: Find contours in the cleaned image
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by area to remove small, noisy detections
    min_contour_area = 50  # Adjust this value as needed
    valid_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]

    # Step 6: Visualize contours on the original image
    contour_image = image.copy()
    cv2.polylines(contour_image, [polygon], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.drawContours(contour_image, valid_contours, -1, (255, 0, 0), 2)

    # Step 7: Calculate the filled area
    filled_area = sum(cv2.contourArea(contour) for contour in valid_contours)
    total_area = cv2.contourArea(polygon)
    fill_ratio = filled_area / total_area if total_area > 0 else 0

    # Overlay information on the final image
    result_image = contour_image.copy()
    cv2.putText(result_image, f"Filled Area: {int(filled_area)} px", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(result_image, f"Total Area: {int(total_area)} px", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(result_image, f"Fill Ratio: {fill_ratio:.2%}", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display all intermediate results in a 2x2 grid
    step1 = cv2.resize(masked_image, (300, 300))
    step2 = cv2.resize(cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR), (300, 300))
    step3 = cv2.resize(cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR), (300, 300))
    step4 = cv2.resize(result_image, (300, 300))

    # Combine images in 2x2 grid
    top_row = np.hstack([step1, step2])
    bottom_row = np.hstack([step3, step4])
    combined = np.vstack([top_row, bottom_row])

    # Show the combined results
    cv2.imshow("Processing Steps", combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Define the polygon coordinates (queue_box)
queue_box = [(564, 507), (470, 488), (816, 141), (869, 153)]

# Load the image
image = cv2.imread("../data/ricks-frame.jpg")

# Analyze the filled area
analyze_filled_area_fixed(image, queue_box)
