import os
import screeninfo
from zoomto.core.driver import ZoomWindowDriver, zoomDriver, clickMaps
from zoomto.utils import SingletonMeta
import typing
import pyautogui as ag
from time import sleep
import pygetwindow as gw

class ZoomToWnd(metaclass=SingletonMeta):
    def __init__(self):
        self._meetingWnd = zoomDriver.getMeetingWnd()
        self._meetingDri = ZoomWindowDriver(self._meetingWnd)

    def sharescreen(
        self,
        option1 : typing.Literal["Basic", "Advanced", "Files", "Apps"],
        option2 : dict,
    ):
        self._meetingDri.activate()
        ag.hotkey('alt', 's')
        selectDialog = zoomDriver.waitForContainStr("select a window")
        selectDriver = ZoomWindowDriver(selectDialog)
        sleep(0.5)
        selectDriver.action(
            clickMaps["single"], f"shareScreen_1_Select{option1}", text=option1
        )
        sleep(0.2)
        selectDriver.action(
            clickMaps["double"], None, **option2
        )
    
class ZoomTo(metaclass=SingletonMeta):
    def __init__(self):
        self._meetingWnd = zoomDriver.getMeetingWnd()
        self._meetingDri = ZoomWindowDriver(self._meetingWnd)
    
    def share_video(
        self,
        path : str,
        send_to_monitor : int = None,
        maximize : bool = True
    ):
        self._meetingDri.activate(nosave=True)
        ag.hotkey('alt', 's')
        selectDialog = zoomDriver.waitForContainStr("select a window")
        selectDriver = ZoomWindowDriver(selectDialog)
        sleep(0.5)
        selectDriver.action(
            clickMaps["single"], "shareScreen_1_SelectAdvanced", text="Advanced"
        )
        sleep(0.2)
        selectDriver.action(
            clickMaps["double"], "shareScreen_2_SelectVideo", 
            image="%zoomto%/sharescreen_advanced_video.png",
            text="Video"
        )
        
        openDialog = zoomDriver.waitForContainStr("open")
        openDriver = ZoomWindowDriver(openDialog)
        openDriver.activate()

        ag.typewrite(os.path.abspath(path))
        ag.hotkey('enter')
        
        sleep(1)
        videoWnd = gw.getActiveWindow()
        if send_to_monitor is not None:
            videoWnd.moveTo(
                screeninfo.get_monitors()[send_to_monitor].x,
                screeninfo.get_monitors()[send_to_monitor].y
            )
            
        if maximize:
            videoWnd.maximize()
            
        sleep(0.5)
        ag.hotkey('space')
        