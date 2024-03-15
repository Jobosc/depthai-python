#!/usr/bin/env python3

from depthai_sdk import OakCamera, RecordType
import depthai as dai
from typing import Dict


def run():
    with OakCamera() as oak:
        color = oak.camera(source=dai.CameraBoardSocket.CAM_A, resolution=dai.ColorCameraProperties.SensorResolution.THE_800_P, fps=20, encode=dai.VideoEncoderProperties.Profile.H265_MAIN, name="color")
        left = oak.camera('left')
        right = oak.camera('right')
        stereo = oak.stereo(left=left, right=right, resolution=dai.ColorCameraProperties.SensorResolution.THE_800_P, fps=20, encode=dai.VideoEncoderProperties.Profile.H265_MAIN, name="color")
        stereo.set_auto_ir(auto_mode=True, continuous_mode=True)
        
        # Synchronize & save all (encoded) streams
        oak.record([color.out.encoded, stereo.out.encoded], './', RecordType.VIDEO)
        oak.visualize([color.out.camera, stereo.out.depth], fps=True, scale=2/3)
        oak.start(blocking=True)


if __name__ == "__main__":
    run()