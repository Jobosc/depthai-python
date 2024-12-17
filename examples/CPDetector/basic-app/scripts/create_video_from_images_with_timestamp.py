import numpy as np
data = np.load('/Users/johnuroko/Documents/Repos/Private/OakDVideoRecorder/Videorecording/20241217/DepthFrames.npy')
print(data.max())
print(data.mean())
print(data.shape)

import cv2
import os
from datetime import datetime

def create_video_from_images_with_timestamps(image_folder, output_video_path):
    # Get list of images and their timestamps
    images = [(img, datetime.strptime(f"{img.split('.')[0]}.{img.split('.')[1]}", '%Y-%m-%dT%H;%M;%S.%f+01;00')) for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort(key=lambda x: x[1])  # Ensure the images are in the correct order based on timestamp

    # Calculate the frame rate
    if len(images) > 1:
        time_diffs = [(images[i+1][1] - images[i][1]).total_seconds() for i in range(len(images) - 1)]
        avg_time_diff = sum(time_diffs) / len(time_diffs)
        fps = 1 / avg_time_diff
    else:
        fps = 30  # Default to 30 FPS if only one image

    # Read the first image to get the frame size
    frame = cv2.imread(os.path.join(image_folder, images[0][0]))
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID'
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for image, timestamp in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        video.write(frame)

    video.release()
    cv2.destroyAllWindows()

# Example usage
create_video_from_images_with_timestamps("output/[2024-12-15T00;22;12.167644+01;00][30FPS]", '/Users/johnuroko/Downloads/depthai-aligned-depth-recording-main/output/video.mp4')
