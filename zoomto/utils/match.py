import numpy as np
from PIL import Image
from typing_extensions import TypedDict
import typing
import pyautogui
import pygetwindow as gw
import easyocr
from zoomto.core.config import GLOBAL_CONFIG, ZoomConfig
from zoomto.utils.debug import debug_image, debug_red_bounding

class matchOptions(TypedDict):
    text : typing.Optional[str]
    image : typing.Optional[typing.Union[str, np.ndarray, Image.Image]]

def capture_window(window: gw.Window):
    window.activate()  # Bring the window to the front
    # Adjust if the window has a border or title bar
    left, top, width, height = window.left, window.top, window.width, window.height
    img =  pyautogui.screenshot(region=(left, top, width, height))
    return np.array(img)


def find_word_coordinates(image, search_word):
    # Create a reader object
    reader = easyocr.Reader(['en'])  # 'en' denotes English language

    # Perform OCR on the image
    results = reader.readtext(image)

    # List to store coordinates of found words
    found_word_coordinates = []

    # Iterate over OCR results
    for result in results:
        # Each result has this format: (bbox, text, confidence)
        bbox, text, _ = result

        # Check if the detected text matches the search word
        if text.lower() == search_word.lower():
            # bbox is in the format [(top_left), (top_right), (bottom_right), (bottom_left)]
            # You can format it as you like, here's a simple conversion to (x, y, width, height)
            top_left = bbox[0]
            bottom_right = bbox[2]
            x, y = top_left
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]

            found_word_coordinates.append((x, y, width, height))

    return found_word_coordinates

def match_text(
    text : str, win : gw.Window,
    config : ZoomConfig = GLOBAL_CONFIG
):
    if text == "":
        return

    res = capture_window(win)
    if config and config.debug_image:
        debug_image(res)

    data = find_word_coordinates(res, text)

    if config.debug_image:
        debug_red_bounding(data, res)

    if len(data) == 0:
        return
    
    coord : typing.Tuple[int, int, int, int] = data[0]

    x = coord[0] + coord[2] / 2
    y = coord[1] + coord[3] / 2

    if config.debug_log:
        print(f"Found {text} at {x}, {y}")

    # x, y + screen

    x = win.left + x
    y = win.top + y
    
    return (x, y)
