from depthai_sdk import OakCamera, RecordType
import datetime

with OakCamera() as oak:
    color = oak.create_camera('color', resolution="800p", encode="H265")

    day = datetime.datetime.now().strftime("%Y%m%d")
    oak.record(outputs=[color.out.encoded], path=f"./VideoRecordings/{day}/", record_type=RecordType.VIDEO)
    # Show color stream
    oak.visualize([color.out.camera], fps=True, scale=2/3)
    oak.start(blocking=False)

    while oak.running():
        key = oak.poll()
        if key == ord('i'):
            color.control.exposure_time_down()
        elif key == ord('o'):
            color.control.exposure_time_up()
        elif key == ord('k'):
            color.control.sensitivity_down()
        elif key == ord('l'):
            color.control.sensitivity_up()

        elif key == ord('e'): # Switch to auto exposure
            color.control.send_controls({'exposure': {'auto': True}})