import os
import typing
from typing_extensions import TypedDict
from zoomto._internal import DIR_PATH
import pygetwindow as gw
from zoomto._internal.onChangeDict import OnChangeSaveDict
from zoomto.utils.misc import load_json

class Coord(TypedDict):
    winX : int
    winY : int
    x : float
    y : float

_match_coords : typing.Dict[str, Coord] = OnChangeSaveDict(
    os.path.join(DIR_PATH, "match_coords.json"),
    load_json(os.path.join(DIR_PATH, "match_builtin.json"))
)

def get_matched_coord(key: str, win : gw.Window):
    global _match_coords
    if key not in _match_coords:
        return None

    coord = _match_coords[key]

    # resize size of window to match
    if coord["winX"] != win.width or coord["winY"] != win.height:
        win.resizeTo(coord["winX"], coord["winY"])

    x = win.left + coord["x"]
    y = win.top + coord["y"]
    return (x, y)

def set_coord(key: str, coord: Coord):
    _match_coords[key] = coord

__all__ = [
    "Coord",
    "get_matched_coord",
    "set_coord",
]