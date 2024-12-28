import os
import subprocess
import cv2
import sys
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
        return None
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("grep_scanned_image_1.png", gray)
    
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
        print(f"No non-white areas found in image.")
        return None
    
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
    # cv2.imwrite("grey_blur.png", gray)
 
    ret,th1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    th2 = cv2.adaptiveThreshold(th1,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY,11,2)
    th3 = cv2.adaptiveThreshold(th1,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)
    # cv2.imwrite("gre_removal_1_grey.png", gray)
    # cv2.imwrite("gre_removal_2_treshold.png", th1)
    # cv2.imwrite("gre_removal_3_treshold.png", th2)
    # cv2.imwrite("gre_removal_4_treshold.png", th3)
    
    # Find contours in the expanded binary mask
    contours, _ = cv2.findContours(th2, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    # th4 = cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite("gre_removal_5_treshold.png", th4)
    
    if not contours:
        print(f"No non-white areas found.")
        return None, None
    
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
        print("Failed to get the largest contour!")
        return img, [0, 0, image_width, image_height]
    
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
    return cropped_image, [x, y, w, h]

def make_image_data(n):
    """Returns the image data lists as bytes"""
    print("\n= Scanning Images =")
    input(f"Press Enter to scan image #{n} front...")
    result = subprocess.run(["scanimage", "--device-name=brother5:bus2;dev1", "--resolution=600", "--format=png", f"--out=./dad_orig/scan_{n}_front.png"], capture_output=True, text=True)
    # input(f"Press Enter to scan image #{n} back...")
    # result = subprocess.run(["scanimage", "--device-name=brother5:bus2;dev1", "--resolution=600", "--format=png", f"--out=./scan2_orig/scan_{n}_back.png"], capture_output=True, text=True)
    return result.stderr

def scan_image_loop(n):
    print("==========")
    print(make_image_data(n))

    print("\n= Cropping Images =")
    front_orig = cv2.imread(f"./dad_orig/scan_{n}_front.png")
    cropped = remove_white_space_area(front_orig, offset=False, offsetMeasure=100)
    if cropped is None:
        print(f"Failed to remove white space of {n}")
        sys.exit()
    final_crop, _ = remove_grey_space(cropped, offset=False, offsetMeasure=100)
    # if final_crop is None or specs is None:
    if final_crop is None:
        print(f"Failed to remove the grey space of {n}")
        sys.exit()
    cv2.imwrite(f"./dad_crop/scan_{n}_front.png", final_crop)

    # print("\n= Cropping Back Image =")
    # #  [x, y, w, h]
    # back_orig = cv2.imread(f"./scan2_orig/scan_{n}_back.png")
    # back_crop = back_orig[specs[1]:specs[1] + specs[3], specs[0]:specs[0] + specs[2]]
    # cv2.imwrite(f"./scan2_crop/scan_{n}_back.png", back_crop)

    scan_image_loop(n+1)

# def make_image_data(n):
#     """Returns the image data lists as bytes"""
#     result = subprocess.run(["scanimage", "--device-name=brother5:bus2;dev1", "--resolution=600", "--format=png", f"--out=./text_scans/scan_{n}.png"], capture_output=True, text=True)
#     return result.stderr

# def scan_image_loop(n):
#     print("==========")
#     input(f"Press Enter to scan image #{n}...")
#     print(make_image_data(n))
#     print("\n= Cropping Image =")
#     # img = cv2.imread(f"./text_scans/scan_{n}.png")
#     # cropped = remove_white_space_area(img, offset=True, offsetMeasure=100)
#     # final_crop = remove_grey_space(cropped, offset=True, offsetMeasure=100)
#     # cv2.imwrite(f"./text_scans/scan_{n}.png", final_crop)
#     scan_image_loop(n+1)

if __name__ == "__main__":
    scan_image_loop(23)