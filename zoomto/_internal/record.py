import os
from zoomto.utils import OnChangeSaveDict
from typing_extensions import TypedDict
import pygetwindow as gw

class Coord(TypedDict):
    winTitle : str
    winWidth : int
    winHeight : int
    x : float
    y : float

record_dict = OnChangeSaveDict(
    os.path.join(os.getcwd(), "record.json"),
)
    
def get_record(wnd : gw.Window, key : str)-> Coord:
    res : Coord = record_dict.get(key, None)
    
    if res is None:
        return None
    
    if res["winHeight"] != wnd.height or \
        res["winWidth"] != wnd.width or \
        res["winTitle"].lower() != wnd.title.lower():
        return None
    
    x = wnd.left + res["x"]
    y = wnd.top + res["y"]

    return (x, y)

def set_record(key: str, wnd : gw.Window, xy : tuple):
    x = float(xy[0] - wnd.left)
    y = float(xy[1] - wnd.top)
    cobj = Coord(
        winTitle = wnd.title,
        winWidth = wnd.width,
        winHeight = wnd.height,
        x = x,
        y = y,
    )
    
    record_dict[key] = cobj