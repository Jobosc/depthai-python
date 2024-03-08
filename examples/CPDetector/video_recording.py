#!/usr/bin/env python3

"""
Video recording script is based on the following scripts:
- VideoEncoder/encoding_max_limit
- StereoDepth/rgb_depth_aligned
- ColorCamera/rgb_preview
- StereoDepth/depth_preview
- Script/script_forward_frames
"""

import cv2
import numpy as np
from utils.camera_settings import CameraSettings
import depthai as dai
from utils.parser import ENVParser

def run():
    env_parser = ENVParser()

    # Prepare camera
    cs = CameraSettings()
    cs.setup_pipeline()

    pipeline = cs.pipeline
    #depthWeight = cs.depthWeight
    rgbWeight = env_parser.rgb_weight

    def updateBlendWeights(percent_rgb):
        """
        Update the rgb and depth weights used to blend depth/rgb image

        @param[in] percent_rgb The rgb weight expressed as a percentage (0..100)
        """
        global depthWeight
        global rgbWeight
        rgbWeight = float(percent_rgb)/100.0
        depthWeight = 1.0 - rgbWeight

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:

        frameRgb = None
        frameDisp = None
        
        print('Connected cameras:', device.getConnectedCameraFeatures())
        # Print out usb speed
        print('Usb speed:', device.getUsbSpeed().name)
        # Bootloader version
        if device.getBootloaderVersion() is not None:
            print('Bootloader version:', device.getBootloaderVersion())
        # Device name
        print('Device name:', device.getDeviceName(), ' Product name:', device.getProductName())
        
        # Configure windows; trackbar adjusts blending ratio of rgb/depth
        blendedWindowName = "rgb-depth"
        cv2.namedWindow(blendedWindowName)
        cv2.createTrackbar('RGB Weight %', blendedWindowName, int(rgbWeight*100), 100, updateBlendWeights)

        ## Queues for storing videos in files
        rgbQueue = device.getOutputQueue('rgbEncode', maxSize=30, blocking=True)
        disparityQueue = device.getOutputQueue('disparityEncode', maxSize=30, blocking=True)
        ## Queues for displaying videos on screen
        disparityQueueDisplay = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)
        rgbQueueDisplay = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        
        # Processing loop
        with open('color.h265', 'wb') as fileColorH265, open('disparity.h264', 'wb') as fileDisparityH264:
            print("Press Ctrl+C to stop encoding...")
            while True:
                ## Store videos
                try:
                    # Empty each queue
                    while disparityQueue.has():
                        disparityQueue.get().getData().tofile(fileDisparityH264)

                    while rgbQueue.has():
                        rgbQueue.get().getData().tofile(fileColorH265)
                except KeyboardInterrupt:
                    break

                frame = rgbQueueDisplay.get()
                if frame is not None:
                    frameRgb = frame.getCvFrame()
                    cv2.imshow("rgb", frameRgb)

                frame = disparityQueueDisplay.get()
                if frame is not None:
                    frameDisp = frame.getFrame()
                    maxDisparity = cs.maxDisparity
                    # Optional, extend range 0..95 -> 0..255, for a better visualisation
                    frameDisp = (frameDisp * 255. / maxDisparity).astype(np.uint8)
                    # Optional, apply false colorization
                    frameDisp = cv2.applyColorMap(frameDisp, cv2.COLORMAP_HOT)
                    frameDisp = np.ascontiguousarray(frameDisp)
                    cv2.imshow("depth", frameDisp)

                """
                # Blend when both received
                if frameRgb is not None and frameDisp is not None:
                    # Need to have both frames in BGR format before blending
                    if len(frameDisp.shape) < 3:
                        frameDisp = cv2.cvtColor(frameDisp, cv2.COLOR_GRAY2BGR)
                    blended = cv2.addWeighted(frameRgb, rgbWeight, frameDisp, depthWeight, 0)
                    cv2.imshow(blendedWindowName, blended)
                    frameRgb = None
                    frameDisp = None
                """

                if cv2.waitKey(1) == ord('q'):
                    break

        print("To view the encoded data, convert the stream file (.h264/.h265) into a video file (.mp4), using commands below:")
        cmd = "ffmpeg -framerate 25 -i {} -c copy {}"
        print(cmd.format("disparity.h264", "disparity.mp4"))
        print(cmd.format("color.h265", "color.mp4"))

if __name__ == "__main__":
    run()