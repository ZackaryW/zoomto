import os
from zoomto.utils import OnChangeSaveDict
import typing
from typing_extensions import TypedDict
import pygetwindow as gw

class Coord(TypedDict):
    winX : int
    winY : int
    x : float
    y : float
    weight : int
    
_records : dict = OnChangeSaveDict(
    os.path.join(os.getcwd(), "records.json")
)

def get_record(title : str, wnd : gw.Window, expectedOutcome : typing.Callable = None) -> typing.List[Coord]:
    if title not in _records:
        return
    
    # filter matching width and height
    availMatches = [coord for coord in _records[title] if coord["winX"] == wnd.width and coord["winY"] == wnd.height]
    
    target = None
    if len(availMatches) == 0:
        for match in _records[title]:
            try:
                wnd.resizeTo(match["winX"], match["winY"])
            except Exception:
                continue
            
            if expectedOutcome and not expectedOutcome():
                continue
            
            target = match
    else:
        # sort them by weight
        availMatches.sort(key=lambda coord : coord["weight"], reverse=True)
        target = availMatches[0]
        
    x = wnd.left + target["x"]
    y = wnd.top + target["y"]
    
    return (x, y)

def set_record(title : str, coords : typing.List[Coord]):
    _records[title] = coords
    
def set_one_record(
    title : str, 
    x : float,
    y : float, 
    wnd : gw.Window,
    parse_rel : bool = True
):
    if parse_rel:
        x = float(x - wnd.left)
        y = float(y - wnd.top)
    
    cobj = Coord(
        winX = wnd.width,
        winY = wnd.height,
        x = x,
        y = y,
        weight = 1
    )
    
    if "title" not in _records:
        _records[title] = [cobj]
    else:
        _records[title] = [cobj] + _records[title]
        
