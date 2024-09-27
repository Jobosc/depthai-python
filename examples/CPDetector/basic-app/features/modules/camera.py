import datetime
import os
import time

import cv2
import depthai as dai
from depthai_sdk import OakCamera, RecordType
from dotenv import load_dotenv

from features.modules.light_barrier import LightBarrier

load_dotenv("/home/pi/depthai-python/examples/CPDetector/basic-app/.env")

temp_path = os.getenv("TEMP_STORAGE")
date_format = os.getenv("DATE_FORMAT")


class Camera(object):
    _instance = None
    running = False
    encode = None
    fps = None
    _ready = False
    _mode = False

    def __new__(cls):
        if cls._instance is None:
            print("Creating the camera object")
            cls._instance = super(Camera, cls).__new__(cls)
            cls.encode = dai.VideoEncoderProperties.Profile.H265_MAIN
            cls.fps = 40
        return cls._instance

    def run(self, block=False) -> int:
        self.running = True
        # camera_led.set(STATUS["recording"])

        state = LightBarrier()

        with OakCamera() as oak:
            # Define cameras
            color = oak.camera(
                source=dai.CameraBoardSocket.CAM_A,
                resolution=dai.ColorCameraProperties.SensorResolution.THE_1080_P,
                fps=self.fps,
                encode=self.encode if self.mode else None,
            )

            stereo = oak.stereo(
                resolution=dai.MonoCameraProperties.SensorResolution.THE_800_P,
                fps=self.fps,
                encode=self.encode,
            )
            # Set IR brightness
            # Turned off IR because of the possible marker disruptions
            stereo.set_auto_ir(auto_mode=False, continuous_mode=False)
            stereo.set_ir(0, 0)

            # Synchronize & save all (encoded) streams
            if self.mode:
                print("Record video without stream.")
                # Folder parameters
                day = datetime.datetime.now().strftime(date_format)

                oak.record(
                    [color.out.encoded, stereo.out.encoded],
                    os.path.join(temp_path, day),
                    RecordType.VIDEO,
                )
            else:
                print("View video without recording.")
                oak.visualize([color.out.camera, stereo.out.depth], fps=True, scale=1 / 2)

            # oak.show_graph()

            oak.start(blocking=block)
            while oak.running():
                time.sleep(0.001)
                oak.poll()
                if not state.activated or not self.ready:
                    oak.device.close()
                    cv2.destroyAllWindows()

            self.running = False
            # camera_led.set(STATUS["available"])
            return 1

    @property
    def camera_connection(self):
        return False if dai.DeviceBootloader.getAllAvailableDevices() == [] else True

    @property
    def ready(self):
        return self._ready

    @ready.setter
    def ready(self, value: bool):
        self._ready = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: bool):
        self._mode = value


if __name__ == "__main__":
    cam = Camera()
    cam.run()
