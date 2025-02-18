"""
This module provides functionality to manage and operate the camera for recording sessions.

It defines the Camera class which handles the initialization, running, and state management of the camera.

Classes:
    Camera: Manages the camera operations including recording and state management.

Methods:
    run: Starts the camera recording process.
"""
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import cv2
import depthai as dai
import numpy as np

from features.modules.light_barrier import LightBarrier
from utils.parser import ENVParser


class Camera(object):
    """
    Manages the camera operations including recording and state management.

    Attributes:
        _instance (Camera): Singleton instance of the Camera class.
        running (bool): Indicates if the camera is currently running.
        fps (int): Frames per second for the camera.
        _ready (bool): Indicates if the camera is ready.
        _mode (bool): Indicates the mode of the camera (recording or viewing).
    """

    _instance = None
    running = False
    fps = None
    _ready = False
    _mode = False
    _storing_data = False

    def __init__(self):
        self.rgb_frames_path = None
        self.depth_frames_path = None

    def __new__(cls):
        if cls._instance is None:
            logging.debug("Initiate camera instance.")
            cls._instance = super(Camera, cls).__new__(cls)
            cls.fps = 30
        return cls._instance

    def run(self, block=False) -> int:
        """
        Starts the camera recording process.

        Args:
            block (bool): Whether to block the execution until recording is finished. Defaults to False.

        Returns:
            int: Status code indicating the result of the operation.
        """
        logging.info("Start process to record with camera.")
        env = ENVParser()
        state = LightBarrier()

        # Create Pipeline
        pipeline = dai.Pipeline()

        # Define sources and outputs
        color = pipeline.create(dai.node.ColorCamera)
        color.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        color.initialControl.setAutoExposureLimit(2000)
        color.setFps(self.fps)
        color.setCamera("color")

        monoLeft = pipeline.create(dai.node.MonoCamera)
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)
        monoLeft.setFps(self.fps)

        monoRight = pipeline.create(dai.node.MonoCamera)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)
        monoRight.setFps(self.fps)

        stereo = pipeline.create(dai.node.StereoDepth)
        stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        stereo.initialConfig.setMedianFilter(dai.MedianFilter.MEDIAN_OFF)
        dai.RawStereoDepthConfig.PostProcessing.SpeckleFilter()
        # stereo.initialConfig.setDisparityShift(10)
        stereo.setLeftRightCheck(False)  # This is required to align Depth with Color. Otherwise set to False
        stereo.setExtendedDisparity(
            False)  # This needs to be set to False. Otherwise the number of frames differ for depth and color
        stereo.setSubpixel(False)
        # stereo.setSubpixelFractionalBits(5)
        # stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A) #TODO: Check if required

        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)

        if self.mode:  # Recording mode
            # Color output node
            frame_color = pipeline.create(dai.node.XLinkOut)
            frame_color.setStreamName("video")
            color.video.link(frame_color.input)

            # Depth output node
            frame_depth = pipeline.create(dai.node.XLinkOut)
            frame_depth.setStreamName("disparity")
            stereo.depth.link(frame_depth.input)

            logging.info("Record video without stream.")

        else:  # Viewing mode
            color.setIspScale(1, 2)

            xoutGrp = pipeline.create(dai.node.XLinkOut)
            xoutGrp.setStreamName("xout")

            # Sync outputs with each other
            sync = pipeline.create(dai.node.Sync)
            sync.setSyncThreshold(timedelta(milliseconds=50))
            stereo.disparity.link(sync.inputs["disparity"])
            color.video.link(sync.inputs["video"])
            sync.out.link(xoutGrp.input)

            logging.info("View video without recording.")

        with dai.Device(pipeline) as device:
            device.setIrLaserDotProjectorIntensity(1)  # Enhancement of depth perception
            device.setIrFloodLightIntensity(0)  # Enhancement of low light performance
            logging.info("Set camera parameters for recording with OAK camera.")
            device.readCalibration().setFov(dai.CameraBoardSocket.CAM_B, 127)
            device.readCalibration().setFov(dai.CameraBoardSocket.CAM_C, 127)
            self.running = True

            if self.mode:  # Recording mode
                current_state = 0
                disparity_queue = device.getOutputQueue(name="disparity", maxSize=1, blocking=block)
                video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=block)
                depth_frames, rgb_frames, depth_timestamps, rgb_timestamps = [], [], [], []

                # Open a file to save encoded video
                day = datetime.now().strftime(env.date_format)
                os.makedirs(os.path.join(env.temp_path, day), exist_ok=True)
                self.depth_frames_path = os.path.join(env.temp_path, day, "depth_frames")
                os.makedirs(self.depth_frames_path, exist_ok=True)
                self.rgb_frames_path = os.path.join(env.temp_path, day, "rgb_frames")
                os.makedirs(self.rgb_frames_path, exist_ok=True)

                print("Recording started...")
                logging.info(f"Camera started recording at: {datetime.now()}")
                while self.ready:
                    try:
                        if current_state != state.activated:
                            logging.info(
                                f"Light barrier triggered to {'start' if state.activated else 'end'} at: {datetime.now()}")
                            current_state = state.activated

                        if current_state == 1 and len(depth_frames) < self.fps * 10:
                            depth_frame = disparity_queue.get()
                            rgb_frame = video_queue.get()
                            depth_frames.append(depth_frame.getFrame())
                            rgb_frames.append(rgb_frame.getCvFrame())
                            depth_timestamps.append(datetime.now() - (dai.Clock.now() - depth_frame.getTimestamp()))
                            rgb_timestamps.append(datetime.now() - (dai.Clock.now() - rgb_frame.getTimestamp()))

                        elif len(depth_frames) > self.fps:
                            print("Saving frames...")
                            self._storing_data = True
                            self.__save_frames(depth_frames, rgb_frames, depth_timestamps, rgb_timestamps)
                            self._storing_data = False
                            print("Frames saved.")

                            depth_frames, rgb_frames, depth_timestamps, rgb_timestamps = [], [], [], []

                    except:
                        logging.warning("There was an issue storing a time point.")
                        break

            else:  # Viewing mode
                disparityMultiplier = 255.0 / stereo.initialConfig.getMaxDisparity()
                queue = device.getOutputQueue(name="xout", maxSize=30, blocking=block)
                while True:
                    msgGrp = queue.get()
                    for name, msg in msgGrp:
                        frame = msg.getCvFrame()
                        if name == "disparity":
                            frame = (frame * disparityMultiplier).astype(np.uint8)
                            frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
                        cv2.imshow(name, frame)
                    if cv2.waitKey(1) == ord("q") or not self.ready:
                        cv2.destroyAllWindows()
                        break

            self.running = False

            return 1

    def __save_frames(self, depth_frames, rgb_frames, depth_timestamps, rgb_timestamps):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.info(f"Saving frames at: {timestamp}")

        depth_path = os.path.join(self.depth_frames_path, timestamp)
        os.makedirs(depth_path, exist_ok=True)
        rgb_path = os.path.join(self.rgb_frames_path, timestamp)
        os.makedirs(rgb_path, exist_ok=True)
        depth_args = [(frame, depth_path, ts.strftime("%Y%m%d_%H%M%S%f")) for frame, ts in
                      zip(depth_frames, depth_timestamps)]
        rgb_args = [(frame, rgb_path, ts.strftime("%Y%m%d_%H%M%S%f")) for frame, ts in zip(rgb_frames, rgb_timestamps)]

        start = datetime.now()
        with ThreadPoolExecutor() as executor:
            executor.map(_save_single_frame, depth_args + rgb_args)
        print(datetime.now() - start)

        logging.info(f"Frames saved at: {timestamp}")

    @property
    def camera_connection(self) -> bool:
        """
        Checks if the camera is connected.

        Returns:
            bool: True if the camera is connected, False otherwise.
        """
        return False if dai.DeviceBootloader.getAllAvailableDevices() == [] else True

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def storing_data(self) -> bool:
        return self._storing_data

    @ready.setter
    def ready(self, value: bool):
        """
        Sets and Gets the readiness state of the camera.

        Args:
            value (bool): The readiness state to set.
        """
        self._ready = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: bool):
        """
        Sets and Gets the mode of the camera.

        Args:
            value (bool): The mode to set (True for recording, False for viewing).
        """
        self._mode = value


def _save_single_frame(args):
    frame, path, frame_type = args
    np.save(os.path.join(path, f"{frame_type}.npy"), frame)
    logging.debug(f"Frame {frame_type}.npy saved at: {datetime.now()}")


if __name__ == "__main__":
    from features.file_operations.video_processing import convert_npy_files_to_video
    from features.file_operations.delete import delete_temporary_recordings

    delete_temporary_recordings()

    cam = Camera()
    cam.ready = True
    cam.mode = True
    cam.run()

    if cam.mode:
        env = ENVParser()
        day = datetime.now().strftime(env.date_format)
        convert_npy_files_to_video(os.path.join(env.temp_path, day, "depth_frames"), "depth.mp4", True)
        convert_npy_files_to_video(os.path.join(env.temp_path, day, "rgb_frames"), "rgb.mp4", False)
