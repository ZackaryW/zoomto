
from time import sleep
import time

import pyautogui
from zoomto.utils.cache import TimelyCachedProperty
from zoomto.utils.misc import (
    get_pid_from_hwnd, get_zoom_process)
import pygetwindow as gw
import typing
import psutil

_excluded_titles = [
    'ZMonitorNumberIndicator'
]

class ZoomProc:
    def __init__(self):
        self.__meeting = get_zoom_process()
        if self.__meeting is None:
            raise ValueError("Zoom meeting process not found")

    @TimelyCachedProperty(timeout=3)
    def proc(self)-> psutil.Process:
        if self.__meeting.status() != psutil.STATUS_RUNNING:
            raise ValueError("Zoom meeting process has either exited or crashed")
        return self.__meeting


    def _direct_window_proc_maps(self)-> typing.List[
        typing.Tuple[gw.Window, psutil.Process, psutil.Process]
    ]:
        res = []
        for window in gw.getAllWindows():
            window : gw.Window

            if window.width == 0:
                continue

            if window.title == "":
                continue
                
            if window.title in _excluded_titles:
                continue

            tpid = get_pid_from_hwnd(window._hWnd)

            if tpid == self.proc.pid:
                res.append((window, self.__meeting, None))
                continue

            for child in self.__meeting.children(recursive=True):
                if  tpid == child.pid:
                    res.append((window, child, child.parent()))

        return res

    @TimelyCachedProperty(timeout=3)
    def window_proc_maps(self):
        return self._direct_window_proc_maps()
    
    @property
    def windows(self):
        return [x[0] for x in self.window_proc_maps]
    
    @property
    def meeting_window(self):
        wnd = self.get_window("Zoom Meeting Participant")
        if wnd is None:
            wnd = self.get_window('VideoFrameWnd')
        if wnd is None:
            wnd = self.get_window("Zoom Meeting")
        
        return wnd

    @property
    def procsWithWindows(self):
        return [x[1] for x in self.window_proc_maps]
    
    def get_window(self, title : str, contains : bool = True, checkLowercase : bool = True):
        for window, *_ in self.window_proc_maps:
            window : gw.Window
            query = title.lower() if checkLowercase else title
            winTitle = window.title.lower() if checkLowercase else window.title

            if contains and query in winTitle:
                return window

            if query == winTitle:
                return window

    def has_subwindows(self, window : gw.Window):
        pid = get_pid_from_hwnd(window._hWnd)
        for _, child, parent in self.window_proc_maps:
            if parent is None:
                continue

            if pid == parent.pid:
                return True
  
    def exit_to_meeting(self, max_depth : int = 5):
        while self.meeting_window != gw.getActiveWindow():
            pyautogui.hotkey("esc")
            sleep(0.3)
            max_depth -= 1
            if max_depth == 0:
                break

    def refresh_now(self):
        TimelyCachedProperty.reset(self, "window_proc_maps")
        TimelyCachedProperty.reset(self, "proc")

    def wait_till_window_count_changes(self, timeout : float = 5, refreshInterval : float = 0.5):
        starting_count = len(self.windows)
        starting_time = time.time()
        while True:

            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window count to change")
            
            current_windows = self._direct_window_proc_maps()

            if len(current_windows) != starting_count:
                return
            
            sleep(refreshInterval)

    def close_all(self):
        for window in self.windows:
            window.close()

    def wait_till_window(
        self, title : str, 
        contains : bool = True, 
        checkLowercase : bool = True,
        timeout : float = 5,
        refreshInterval : float = 0.5
    ):
        starting_time = time.time()

        while True:
            
            maps = self._direct_window_proc_maps()
            for window, *_ in maps:
                window : gw.Window
                query = title.lower() if checkLowercase else title
                winTitle = window.title.lower() if checkLowercase else window.title

                if contains and query in winTitle:
                    return window

                if query == winTitle:
                    return window
                
            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window")

            sleep(refreshInterval)
    
    def keep_only_meeting_wnd(self):
        for window in self.windows:
            if window != self.meeting_window:
                window.close()

        sleep(1)

    