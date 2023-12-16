import os
from time import sleep
from zrcl3.singleton import SingletonMeta
import pyautogui as ag
from zoomto.core.driver import RecordOptions, ZoomDriver
from zoomto.core.proc import ZoomProc
import typing
import pygetwindow as gw
import screeninfo

class ZoomTo(metaclass=SingletonMeta):
    def __init__(self):
        self._driver = ZoomDriver()
        self._proc = ZoomProc()
    
    def _sharescreen(
        self,
        option1 : typing.Literal["Basic", "Advanced", "Files", "Apps"],
        option2 : dict,
    ):
        self._proc.keepOnlyMeeting()
        self._driver.activate_window(self._proc.meetingWnd)
        ag.hotkey('alt', 's')
        selection = self._proc.waitTillWindow("select a window")
        sleep(1)
        with self._driver.perform_record(
            "sharescreen", "single", selection
        ) as w:
            w(text=option1)
            
        with self._driver.perform_record(
            "sharescreen_2", "double", selection
        ) as w:
            w(**option2)
            
    def _sharescreen_open(self, path : str):
        ag.typewrite(path)
        ag.hotkey('enter')
        
    def share_video(
        self, path : str,
        send_to_monitor : int = None,
        maximize : bool = True
    ):
        self._sharescreen(
            option1="Advanced",
            option2=dict(
                image="%zoomto%/sharescreen_advanced_video.png",
                text="Video"
            )
        )
        self._sharescreen_open(os.path.abspath(path=path))

        sleep(1)
        wnd = gw.getActiveWindow()

        if send_to_monitor is not None:
            wnd.moveTo(
                screeninfo.get_monitors()[send_to_monitor].x,
                screeninfo.get_monitors()[send_to_monitor].y
            )

        if maximize:
            wnd.maximize()
            
        
        sleep(0.3)
        ag.hotkey('space')