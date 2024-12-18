import cv2
import numpy as np

# Paths to the video files and the .npy file
disparity_video_path = '/Users/johnuroko/Downloads/depth/disparity.mp4'
rgb_video_path = '/Users/johnuroko/Downloads/depth/rgb.mp4'
npy_path = '/Users/johnuroko/Downloads/depth/disparity.npy'

def count_frames(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return 0

    # Get the total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Release the video capture object
    cap.release()

    return total_frames

# Count the number of frames in the videos
frame_count = count_frames(disparity_video_path)
print(f"Total number of disparity frames: {frame_count}")
frame_count = count_frames(rgb_video_path)
print(f"Total number of color frames: {frame_count}")

# Load the .npy file
depth_array = np.load(npy_path)

# Open the video files
disparity_cap = cv2.VideoCapture(disparity_video_path)
rgb_cap = cv2.VideoCapture(rgb_video_path)

# Check if the videos opened successfully
if not disparity_cap.isOpened() or not rgb_cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get the total number of frames in the videos
total_frames = int(disparity_cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Function to display the frames and handle mouse events
def show_frames(frame_number):
    # Set the frame position
    disparity_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    rgb_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frames
    ret_disparity, disparity_frame = disparity_cap.read()
    ret_rgb, rgb_frame = rgb_cap.read()
    if not ret_disparity or not ret_rgb:
        print("Error: Could not read frame.")
        return

    # Display the frames
    cv2.imshow('Disparity Video', disparity_frame)
    cv2.imshow('RGB Video', rgb_frame)

    # Mouse callback function to print pixel values
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            print(f"Pixel value at ({x}, {y}): {depth_array[frame_number, y, x]}")
            # TODO: Calculate depth value from pixel value correctly!!!
            # depth_value = 1280 * (1 / (2 * math.tan((127 / 2) * (math.pi / 180)))) * (7.5 / calc_pixel_value)  # Convert pixel value to depth in centimeters
            # print(f"Pixel value at ({x}, {y}): {pixel_value} - Depth value: {depth_value:.2f} cm")

    # Set the mouse callback function
    cv2.setMouseCallback('Disparity Video', mouse_callback)

# Display a specific frame (e.g., frame number 100)
frame_number = 100
if frame_number < total_frames:
    show_frames(frame_number)
else:
    print(f"Error: Frame number {frame_number} exceeds total frames {total_frames}.")

# Function to handle key events
def handle_key_events():
    global frame_number
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == ord('n'):  # Move to the next frame when 'n' is pressed
            frame_number += 1
            if frame_number < total_frames:
                show_frames(frame_number)
            else:
                print("Reached the end of the video.")
                break
        elif key == ord('q'):  # Quit when 'q' is pressed
            break

# Handle key events
handle_key_events()

# Release the video capture objects and close the windows
disparity_cap.release()
rgb_cap.release()
cv2.destroyAllWindows()