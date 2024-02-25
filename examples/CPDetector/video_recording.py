#!/usr/bin/env python3

import cv2
import numpy as np
from utils.camera_settings import CameraSettings

def run():
    # Prepare camera
    cs = CameraSettings()
    cs.setup_pipeline()

    device = cs.device
    pipeline = cs.pipeline
    stereo = cs.stereo
    #depthWeight = cs.depthWeight
    rgbWeight = cs.rgbWeight

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
    with device:
        device.startPipeline(pipeline)

        frameRgb = None
        frameDisp = None
        
        # Configure windows; trackbar adjusts blending ratio of rgb/depth
        rgbWindowName = "rgb"
        depthWindowName = "depth"
        blendedWindowName = "rgb-depth"
        cv2.namedWindow(rgbWindowName)
        cv2.namedWindow(depthWindowName)
        cv2.namedWindow(blendedWindowName)
        cv2.createTrackbar('RGB Weight %', blendedWindowName, int(rgbWeight*100), 100, updateBlendWeights)

        while True:
            latestPacket = {}
            latestPacket["rgb"] = None
            latestPacket["disp"] = None

            queueEvents = device.getQueueEvents(("rgb", "disp"))
            for queueName in queueEvents:
                packets = device.getOutputQueue(queueName).tryGetAll()
                if len(packets) > 0:
                    latestPacket[queueName] = packets[-1]

            if latestPacket["rgb"] is not None:
                frameRgb = latestPacket["rgb"].getCvFrame()
                cv2.imshow(rgbWindowName, frameRgb)

            if latestPacket["disp"] is not None:
                frameDisp = latestPacket["disp"].getFrame()
                maxDisparity = stereo.initialConfig.getMaxDisparity()
                # Optional, extend range 0..95 -> 0..255, for a better visualisation
                if 1: frameDisp = (frameDisp * 255. / maxDisparity).astype(np.uint8)
                # Optional, apply false colorization
                if 1: frameDisp = cv2.applyColorMap(frameDisp, cv2.COLORMAP_HOT)
                frameDisp = np.ascontiguousarray(frameDisp)
                cv2.imshow(depthWindowName, frameDisp)
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

if __name__ == "__main__":
    run()