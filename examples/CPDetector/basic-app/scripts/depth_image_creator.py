import numpy as np
import cv2

def create_image_from_array(array, output_image_path):
    # Normalize the array to the range 0-255
    normalized_array = cv2.normalize(array, None, 0, 255, cv2.NORM_MINMAX)
    normalized_array = normalized_array.astype(np.uint8)  # Convert to unsigned 8-bit integer type
    #normalized_array = cv2.applyColorMap(array, cv2.COLORMAP_JET)

    # Save the array as an image
    cv2.imwrite(output_image_path, normalized_array)

# Example usage
array = np.load('/Users/johnuroko/Downloads/depthai-aligned-depth-recording-main/output/[2024-12-17T09;22;41.788861+01;00][30FPS]/2024-12-17T09;22;53.379152+01;00.npy')
create_image_from_array(array, '/Users/johnuroko/Downloads/depthai-aligned-depth-recording-main/output/image.png')