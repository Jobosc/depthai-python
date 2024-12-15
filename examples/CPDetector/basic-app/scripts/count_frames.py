import cv2

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

# Example usage
video_path = "/Videorecording/20241215/depth.mp4"
frame_count = count_frames(video_path)
print(f"Total number of disparity frames: {frame_count}")
video_path = "/Videorecording/20241215/rgb.mp4"
frame_count = count_frames(video_path)
print(f"Total number of color frames: {frame_count}")