from functools import cache
import pygetwindow
import screeninfo
from importlib.util import spec_from_file_location, module_from_spec

def activateWnd(wnd: pygetwindow.Window):
    try:
        if wnd.isActive:
            return
        wnd.activate()
    except Exception:
        pass

@cache
def loadBase64Img(string: str):
    import base64
    from PIL import Image
    import io

    if string.startswith("data:image/png;base64,"):
        string = string[22:]
    return Image.open(io.BytesIO(base64.b64decode(string)))

def sendWindowToMonitor(wnd : pygetwindow.Window, monitor : int = 0):
    screen = screeninfo.get_monitors()[monitor]
    centerx = screen.x + int(screen.width / 2)
    centery = screen.y + int(screen.height / 2)
    wnd.move(centerx, centery)


def importlocalFile(file):
    spec = spec_from_file_location("localfile", file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@cache
def getPrimaryMonitor():
    for i, monitor in enumerate(screeninfo.get_monitors()):
        if monitor.is_primary:
            return i
    