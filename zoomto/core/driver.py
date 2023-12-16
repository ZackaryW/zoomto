
from contextlib import contextmanager
import logging
import typing
from typing_extensions import TypedDict, NotRequired
from eel import sleep
from zoomto._internal import IMAGE_DIR
from zrcl3.singleton import SingletonMeta
from zoomto._internal.debug import debug_image, debug_red_bounding
from zoomto._internal.record import get_record, set_one_record
from zoomto.utils import capture_window, find_word_coordinates
from zoomto.core.proc import ZoomProc
import pyautogui
import pygetwindow as gw
from zoomto.core.cfg import config

class RecordOptions(TypedDict):
    text : NotRequired[str]
    image : NotRequired[str]

class RecordProxyObj:
    def __init__(self, title : str, wnd : gw.Window):
        self.title = title
        self.wnd = wnd
        self.res = None
        
    def __call__(self, **kwargs : typing.Unpack[RecordOptions]) -> None:
        driver = ZoomDriver()
        res =driver.match(self.wnd, **kwargs)
        if not res:
            raise ValueError("res should not be None")
        set_one_record(self.title, *res, wnd=self.wnd)
        self.res = res
    
class ZoomDriver(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._proc = ZoomProc()
    
    matchMethods : typing.ClassVar[typing.List[str]] = ["text", "image"]
    clickMaps : dict = {
        "single" : pyautogui.click,
        "double" : pyautogui.doubleClick,
        "rapid" : lambda *args, **kwargs: pyautogui.click(*args, **kwargs, clicks=5),
        "right" : pyautogui.rightClick
    }
    clickTypes = typing.Literal["single", "double", "rapid", "right"]

    def parse_match(self, **kwargs):
        method_sequence = []
        for k, v in kwargs.items():
            if k not in self.matchMethods:
                continue
            method_sequence.append((k, v))
        
        kwargs = {k : v for k, v in kwargs.items() if k not in self.matchMethods}

        return method_sequence, kwargs
    
    def match_image(self, value, wnd : gw.Window):
        if isinstance(value, str):
            value = value.replace("%zoomto%", IMAGE_DIR)
        res = pyautogui.locateOnWindow(image=value, title=wnd.title)
        res = pyautogui.center(res) if res is not None else None
        return res
    
    def match_text(self, text : str, wnd : gw.Window):
        if text == "":
            return
        
        res = capture_window(wnd)
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

        x = wnd.left + x
        y = wnd.top + y
        
        return (x, y)

    def match(self, wnd : gw.Window, **kwargs):
        method_sequence, kwargs = self.parse_match(**kwargs)
        res = None
        for k, v in method_sequence:
            match_method = getattr(self, f"match_{k}")
            res = match_method(v, wnd)
            if res is None:
                continue
        return res
    
    @contextmanager
    def perform_record(
        self, title : str, action : str, wnd : gw.Window
    ):
        if config and config.debug_log:
            logging.info(f"Performing {title}")
        res = get_record(title, wnd)
        
        try:
            if res:
                logging.info(f"Found {title} at {res}")
                self.clickMaps[action](*res)
                yield 
                return
            
            pobj = RecordProxyObj(title, wnd)
            
            yield pobj
        finally:
            if "pobj" not in locals():
                return
            
            if pobj.res:
                self.clickMaps[action](*pobj.res)
            
    def activate_window(self, wnd : gw.Window):
        try:
            wnd.activate()
            # check if process returned 0
        except gw.PyGetWindowException:
            if gw.getActiveWindow() == wnd:
                return
            
            if wnd == self._proc.meetingWnd:
                self.exit_to_meeting()
            
        except Exception as e:
            raise e
        
    def exit_to_meeting(self, max_depth : int = 10):
        while self._proc.meetingWnd != (lastActive := gw.getActiveWindow()):
            pyautogui.hotkey("esc")
            
            if lastActive == gw.getActiveWindow():
                pyautogui.hotkey("esc")
                
            if lastActive == gw.getActiveWindow():
                raise ValueError("Failed to exit to meeting")
            
            if max_depth == 0:
                break
            
            sleep(0.3)
            max_depth -= 1
            
    