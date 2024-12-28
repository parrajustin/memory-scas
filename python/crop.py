import cv2
import numpy as np

# def crop_image(img):
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
#     contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     x, y, w, h = cv2.boundingRect(contours[0])
#     return img[y:y+h, x:x+w]
def remove_white_space_area(image, kernel_size=10, offset=False, offsetMeasure=30):
    """
    Crops the image to the largest bounding box around non-white areas, optionally applying an offset.

    Parameters:
        image_path (str): Path to the input image.
        output_path (str): Path to save the cropped image.
        kernel_size (int): Size of the kernel used for morphological operations to expand areas.
        offset (bool): Whether to apply an offset to the bounding box.
        offsetMeasure (int): Amount of offset to apply if offset is True.
    """
    # Load the image
    # image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Image at could not be loaded.")
        return
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("grep_scanned_image_1.png", gray)
    
    # Define white color range in grayscale
    white_min = 240  # This can be adjusted based on the whiteness threshold
    white_max = 255
    
    # Create a binary mask where non-white areas are 1
    _, binary_mask = cv2.threshold(gray, white_min, white_max, cv2.THRESH_BINARY_INV)
    
    # Apply morphological operations to expand the non-white areas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    expanded_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours in the expanded binary mask
    contours, _ = cv2.findContours(expanded_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print(f"No non-white areas found in {image_path}.")
        return
    
    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the bounding box for the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Apply offset if specified
    if offset:
        x -= offsetMeasure
        y -= offsetMeasure
        w += 2 * offsetMeasure
        h += 2 * offsetMeasure
    
    # Ensure the bounding box coordinates are within image boundaries
    x = max(x, 0)
    y = max(y, 0)
    w = min(w, image.shape[1] - x)
    h = min(h, image.shape[0] - y)
    
    # Crop the image based on the adjusted bounding box
    cropped_image = image[y:y + h, x:x + w]
    return cropped_image

def remove_grey_space(img, offset=False, offsetMeasure=30):
    # fixed = img.img_to_array(img, dtype='uint8')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray,5)
    cv2.imwrite("grey_blur.png", gray)
 
    ret,th1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    th2 = cv2.adaptiveThreshold(th1,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY,11,2)
    th3 = cv2.adaptiveThreshold(th1,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)
    cv2.imwrite("gre_removal_1_grey.png", gray)
    cv2.imwrite("gre_removal_2_treshold.png", th1)
    cv2.imwrite("gre_removal_3_treshold.png", th2)
    cv2.imwrite("gre_removal_4_treshold.png", th3)
    
    # Find contours in the expanded binary mask
    contours, _ = cv2.findContours(th2, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    # th4 = cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite("gre_removal_5_treshold.png", th4)
    
    if not contours:
        print(f"No non-white areas found in {image_path}.")
        return
    
    # Filter the largest contour that is not the size of the whole image
    image_height, image_width = gray.shape
    largest_contour = None
    crop_x = image_width
    crop_y = image_height
    crop_x2 = 0 
    crop_y2 = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        contour_area = cv2.contourArea(contour)

        # Check if the contour is not the size of the whole image
        if (w < image_width and h < image_height and x + w < image_width - 5):
            largest_contour = contour
            crop_x2 = max(crop_x2, x + w)
            crop_y2 = max(crop_y2, y + h)
            crop_x = min(x, crop_x)
            crop_y = min(y, crop_y)


    if largest_contour is None:
        print("Failed!")
        return img
    
    # Find the largest contour
    # largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the bounding box for the largest contour
    # x, y, w, h = cv2.boundingRect(largest_contour)
    x = crop_x
    y = crop_y
    w = crop_x2 - crop_x
    h = crop_y2 - crop_y
    
    # Apply offset if specified
    if offset:
        x -= offsetMeasure
        y -= offsetMeasure
        w += 2 * offsetMeasure
        h += 2 * offsetMeasure
    
    # Ensure the bounding box coordinates are within image boundaries
    x = max(x, 0)
    y = max(y, 0)
    w = min(w, img.shape[1] - x)
    h = min(h, img.shape[0] - y)
    
    # Crop the image based on the adjusted bounding box
    cropped_image = img[y:y + h, x:x + w]
    return cropped_image

print("reading image")
img = cv2.imread("scanned_image_1.png")
print("read image")
cropped = remove_white_space_area(img)
print("crop image")
cv2.imwrite("crop_scanned_image_1.png", cropped)
grey_crop = remove_grey_space(cropped)
cv2.imwrite("crop_scanned_image_2.png", grey_crop)
print("write image")
