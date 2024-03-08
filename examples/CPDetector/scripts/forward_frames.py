ctrl = CameraControl()
ctrl.setCaptureStill(True)
# Initially send still event
node.io['ctrl'].send(ctrl)

normal = True
while True:
    frame = node.io['frames'].get()
    if normal:
        node.io['rgb'].send(frame)
        normal = False
    else:
        node.io['rgbEncode'].send(frame)
        normal = True
    node.io['ctrl'].send(ctrl)