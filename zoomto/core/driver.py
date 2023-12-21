import time
import typing
from typing_extensions import TypedDict
from time import sleep
import pyautogui
from zoomto._internal.debug import debug_image, debug_red_bounding
from zoomto._internal.record import Coord, get_record, set_record
from zoomto._internal.win32 import WindowMgr
from zoomto.utils import (
    SingletonMeta, TimelyCachedProperty, get_pid_from_hwnd, capture_window,
    find_word_coordinates
)
import psutil
import pygetwindow as gw
from zoomto.core.cfg import config
from zoomto._internal import IMAGE_DIR

wmn = WindowMgr()

clickMaps : dict = {
    "single" : pyautogui.click,
    "double" : pyautogui.doubleClick,
    "rapid" : lambda *args, **kwargs: pyautogui.click(*args, **kwargs, clicks=5),
    "right" : pyautogui.rightClick
}

class ZoomWindowDriver:
    def __init__(self, wnd : gw.Window):
        self.wnd = wnd
    
    def match_image(self, value):
        if isinstance(value, str):
            value = value.replace("%zoomto%", IMAGE_DIR)
        res = pyautogui.locateOnWindow(image=value, title=self.wnd.title)
        res = pyautogui.center(res) if res is not None else None
        return res
    
    def match_text(self, text : str):
        if text == "":
            return
        
        res = capture_window(self.wnd)
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

        x = self.wnd.left + x
        y = self.wnd.top + y
        
        return (x, y)
    
    def match(self, **kwargs):
        res = None
        for k, v in kwargs.items():
            match_method = getattr(self, f"match_{k}")
            res = match_method(v)
            if res is None:
                continue
        return res
    
    def action(self, clickMethod : typing.Callable, key : str, **kwargs):
        if key is None:
            coord = None
        else:
            coord : Coord = get_record(self.wnd, key)
        if coord is not None:
            return clickMethod(*coord)
    
        coord = self.match(**kwargs)
        if coord is not None:
            set_record(key, self.wnd, coord)
            return clickMethod(*coord)
    
        raise Exception(f"Could not match {key}")
    
    def activate(self, nosave : bool = False):
        if self.wnd.isActive:
            return
        try:
            self.wnd.activate()
            # check if process returned 0
        except gw.PyGetWindowException:
            if nosave:
                return
            
            try:
                sleep(0.2)
                wmn.find_window_wildcard(self.wnd.title)
                wmn.set_foreground()
                
            except Exception:
                if gw.getActiveWindow() == self.wnd:
                    return
                raise
        except Exception as e:
            raise e
        
class ZoomDriver(metaclass=SingletonMeta):
    _excludedTitles : typing.List[str] = [
        'ZMonitorNumberIndicator',
        ""
    ]
    
    class WinCtx(TypedDict):
        win : gw.Window
        pid : int
        title : str
    
    @TimelyCachedProperty(timeout=999)
    def getProcess(self):
        for proc in psutil.process_iter():
            if proc.name().lower() != "zoom.exe":
                continue

            if len(proc.cmdline()) >1:
                return proc
            
        return None
    
    def getMeetingWnd(self):
        for w in gw.getAllWindows():
            w : gw.Window
            if w.title.startswith("Zoom Meeting Participant"):
                return w
            elif w.title == 'VideoFrameWnd':
                return w
            elif w.title.startswith("Zoom Meeting"):
                return w
    
        raise Exception("Could not find zoom meeting window")
        
    @TimelyCachedProperty(timeout=1)
    def getWindowCtxes(self) -> typing.List[WinCtx]:
        wins = []
        
        for w in gw.getAllWindows():
            w : gw.Window
            if w.title == "":
                continue
            
            if w.title in self._excludedTitles:
                continue
            
            pid = get_pid_from_hwnd(w._hWnd)
            if pid == self.getProcess.pid:
                wins.append(self.WinCtx(win=w, pid=pid, title=w.title))
            
        return wins
    
    def getWindows(self):
        return [w['win'] for w in self.getWindowCtxes]
    
    def getWindowByTitle(self, title):
        for w in self.getWindows():
            if w.title == title:
                return w
            
    def getWindowByContainStr(self, title):
        for w in self.getWindows():
            if title.lower() in w.title.lower():
                return w
    
    def getWindowTitles(self):
        return [w['title'] for w in self.getWindows()]
    
    def waitForTitle(self, title, timeout : float = 6):
        starting_time = time.time() 
        while True:
            sleep(0.2)
            if title in self.getWindowTitles():
                return self.getWindowByTitle(title)
            
            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window")
            
    def waitForContainStr(self, title, timeout : float = 6):
        starting_time = time.time() 
        while True:
            sleep(0.2)
            if any(title.lower() in w.title.lower() for w in self.getWindows()):
                return self.getWindowByContainStr(title)
            
            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window")
            
    def waitForWindow(self, title, timeout : float = 6):
        starting_time = time.time() 
        while True:
            sleep(0.2)
            if title in self.getWindowTitles():
                return self.getWindowByTitle(title)
            
            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window")
    
    
    
    
zoomDriver = ZoomDriver()
