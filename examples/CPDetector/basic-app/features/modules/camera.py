import time
from depthai_sdk import OakCamera, RecordType
import depthai as dai
import datetime
import os

from features.modules.light_barrier import LightBarrier

from dotenv import load_dotenv
import cv2

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
        state = LightBarrier()

        with OakCamera() as oak:
            # Define cameras
            color = oak.camera(
                source=dai.CameraBoardSocket.CAM_A,
                resolution=dai.ColorCameraProperties.SensorResolution.THE_1080_P,
                fps=self.fps,
                encode=self.encode if self.mode else None,
            )

            # Synchronize & save all (encoded) streams
            if self.mode:
                print("Record video without stream.")
                # Folder parameters
                day = datetime.datetime.now().strftime(date_format)

                stereo = oak.stereo(
                    resolution=dai.MonoCameraProperties.SensorResolution.THE_800_P,
                    fps=self.fps,
                    encode=self.encode,
                )
                # Set IR brightness
                stereo.set_auto_ir(auto_mode=True, continuous_mode=True)
                # stereo.set_ir(dot_projector_brightness, flood_brightness)

                oak.record(
                    [color.out.encoded, stereo.out.encoded],
                    os.path.join(temp_path, day),
                    RecordType.VIDEO,
                )
            else:
                print("View video without recording.")
                oak.visualize([color.out.camera], fps=True, scale=1 / 2)

            # oak.show_graph()

            oak.start(blocking=block)
            while oak.running():
                time.sleep(0.001)
                oak.poll()
                if not state.activated or not self.ready:
                    oak.device.close()
                    cv2.destroyAllWindows()

            self.running = False
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
