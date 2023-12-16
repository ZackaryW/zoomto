from PIL import Image, ImageDraw
import numpy as np

def debug_image(image : np.ndarray):
    image = Image.fromarray(image)
    image.show()

def debug_red_bounding(coordinates : list, image : np.ndarray):
    image = Image.fromarray(image)

    draw = ImageDraw.Draw(image)
    for coord in coordinates:
        image : ImageDraw.ImageDraw
        # draw rectangle
        x, y, width, height = coord
        draw.rectangle([(x, y), (x + width, y + height)], fill=None, outline="red", width=2)

    # open
    image.show()