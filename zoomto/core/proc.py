import time
import typing
from typing_extensions import TypedDict
from eel import sleep
import psutil
import pygetwindow as gw
from zoomto.utils import SingletonMeta, get_pid_from_hwnd, TimelyCachedProperty

class ZoomWndCtx(TypedDict):
    window: gw.Window
    proc: psutil.Process
    parentProc: typing.Optional[psutil.Process]
    parentWindow: typing.Optional[gw.Window]

class ZoomProc(metaclass=SingletonMeta):
    @staticmethod
    def getZoomProcess():
        """
        Returns the process object for the currently running Zoom application.
        
        :return: The process object for the currently running Zoom application, or None if Zoom is not running.
        """
        for proc in psutil.process_iter():
            if proc.name().lower() != "zoom.exe":
                continue

            if len(proc.cmdline()) >1:
                return proc
            
        return None

    _excludedTitles : typing.List[str] = [
        'ZMonitorNumberIndicator',
        ""
    ]

    def __init__(self) -> None:
        self.__meeting_proc = self.getZoomProcess()
        # perform one round of checking
        self.proc

    @TimelyCachedProperty(timeout=1)
    def windows(self):
        wins = []

        for window in gw.getAllWindows():
            window : gw.Window

            if window.width == 0:
                continue

            if window.title in self._excludedTitles:
                continue

            tpid = get_pid_from_hwnd(window._hWnd)

            if tpid == self.proc.pid:
                wins.append(window)

        return wins

    @TimelyCachedProperty(timeout=3)
    def proc(self) -> psutil.Process:
        if self.__meeting_proc is None:
            raise ValueError("Zoom meeting process not found")
        if self.__meeting_proc.status() != psutil.STATUS_RUNNING:
            raise ValueError("Zoom meeting process has either exited or crashed")
        return self.__meeting_proc
    

    def getWnd1(
        self, 
        title : str,
        contains : bool = True,
        checkLowercase : bool = True
    ):
        for window in self.windows:
            window : gw.Window
            query = title.lower() if checkLowercase else title
            winTitle = window.title.lower() if checkLowercase else window.title
            if contains and query in winTitle:
                return window
            elif not contains and query == winTitle:
                return window
            
        return None

    @property
    def meetingWnd(self):
        wnd = self.getWnd1("Zoom Meeting Participant")
        if wnd is None:
            wnd = self.getWnd1('VideoFrameWnd')
        if wnd is None:
            wnd = self.getWnd1("Zoom Meeting")
        
        return wnd
    
    def keepOnlyMeeting(self):
        for window in self.windows:
            if window != self.meetingWnd:
                window.close()
                
        sleep(1)
        
    def waitTillWindowCountChanges(self, timeout : float = 5, refreshInterval : float = 0.5):
        starting_count = len(self.windows)
        starting_time = time.time()
        while True:

            if time.time() - starting_time > timeout:
                raise ValueError("Timed out while waiting for window count to change")
            
            if len(self.windows) != starting_count:
                return
            
            sleep(refreshInterval)
            
    def waitTillWindow(
        self, title : str, 
        contains : bool = True, 
        checkLowercase : bool = True,
        timeout : float = 6,
        refreshInterval : float = 1
    ):
        starting_time = time.time()

        while True:
            for window in self.windows:
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