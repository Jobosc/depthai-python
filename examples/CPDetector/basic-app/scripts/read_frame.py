import cv2
import numpy as np

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        # Get the pixel value at (x, y)
        pixel_value = param[y, x]
        print(f"Pixel value at ({x}, {y}): {pixel_value}")

def read_disparity_frame(video_path, frame_number):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame
    ret, frame = cap.read()

    # Release the video capture object
    cap.release()

    if not ret:
        print(f"Error: Could not read frame {frame_number}.")
        return None

    # Convert the frame to grayscale if it is not already
    if len(frame.shape) == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    return frame

# Example usage
video_path = '/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20241126/6-1944301031BBED1200/disparity.mp4'
frame_number = 10  # Frame number to read
disparity_frame = read_disparity_frame(video_path, frame_number)

if disparity_frame is not None:
    print(f"Disparity frame {frame_number} values:\n{disparity_frame}")
    # Display the frame
    cv2.imshow('Disparity Frame', disparity_frame)
    cv2.setMouseCallback('Disparity Frame', mouse_callback, disparity_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()