# overload pyautogui

import PIL
import PIL.Image
import pyautogui
from zoomto.utils import loadBase64Img

originalXYArgs = pyautogui._normalizeXYArgs

def _normalizeXYArgs(x, y):
    if isinstance(x, str) and x.startswith("data:image/png;base64,"):
        x = loadBase64Img(x)

    if isinstance(x, PIL.Image.Image):
        try:
            location = pyautogui.locateOnScreen(x)
            # The following code only runs if pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION is not set to True, meaning that
            # locateOnScreen() returns None if the image can't be found.
            if location is not None:
                return pyautogui.center(location)
            else:
                return None
        except pyautogui.ImageNotFoundException:
            raise pyautogui.ImageNotFoundException

    return originalXYArgs(x, y)

pyautogui._normalizeXYArgs = _normalizeXYArgs