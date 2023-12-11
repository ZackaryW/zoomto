
from time import sleep
import typing
from zoomto._internal import IMAGE_DIR
from zoomto._internal.record import Coord, get_matched_coord, set_coord
from zoomto.core.config import GLOBAL_CONFIG, ZoomConfig
from zoomto.core.proc import ZoomProc
import pyautogui
import pygetwindow as gw
import screeninfo

from zoomto.utils.match import match_text, matchOptions

click_maps = {
    "single" : pyautogui.click,
    "double" : pyautogui.doubleClick,
    "rapid" : lambda *args, **kwargs: pyautogui.click(*args, **kwargs, clicks=5),
    "right" : pyautogui.rightClick
}

click_types = typing.Literal["single", "double", "rapid", "right"]

class ZoomTo:
    config : ZoomConfig = GLOBAL_CONFIG

    def __click_action(
        self, 
        key: str, 
        win : gw.Window,
        clickType : click_types, 
        **kwargs : typing.Unpack[matchOptions]
    ):
        res = get_matched_coord(key, win)
        if res is not None:
            click_maps[clickType](*res)
            print(f"{clickType} {key} at {res}")
            return

        priority = {k : v for k, v in kwargs.items() if k in matchOptions.__annotations__}
        for k, v in priority.items():
            try:
                match k:
                    case "text":
                        res = match_text(v, win)
                    case "image":
                        v = v.replace("%zoomto%", IMAGE_DIR)
                        res = pyautogui.locateOnWindow(v, win.title)
                        res = pyautogui.center(res) if res is not None else None

                if res is None:
                    continue
                print(f"{clickType} {key} at {res}")
                click_maps[clickType](*res)
            except Exception:
                continue
        
            set_coord(key, Coord(
                x=float(res[0] - win.left),
                y=float(res[1] - win.top),
                winX=win.width,
                winY=win.height
            ))
            return

    def __init__(self):
        self.__zproc = ZoomProc()
        if self.__zproc.meeting_window is None:
            raise ValueError("Zoom meeting window not found")

    def __activate_window(
        self, 
        win : gw.Window, 
        reattempt : bool = True,
    ):
        try:
            win.activate()
            # check if process returned 0
        except gw.PyGetWindowException:
            if gw.getActiveWindow() == win:
                return
            
            # check if it has sub windows
            if reattempt:
                self.__zproc.exit_to_meeting()
            else:
                raise
            sleep(0.5)
            win.activate()
            sleep(2)
        except Exception as e:
            raise e
        
    def _shareScreen(
        self, 
        option1 : typing.Literal["Basic", "Advanced", "Files", "Apps"],
        option2 : matchOptions,
        share_sound : bool = None,
        optimize_for_video_clip : bool = None
    ):
        self.__zproc.keep_only_meeting_wnd()
        self.__activate_window(self.__zproc.meeting_window)
        pyautogui.hotkey('alt', 's')
        selection_window = self.__zproc.wait_till_window("select a window", refreshInterval=1)
        sleep(1)
        self.__click_action(
            key="sharescreen_menu",
            win=selection_window,
            clickType="single",
            text=option1
        )

        sleep(0.1)

        self.__click_action(
            key="sharescreen_secondary_option",
            win=selection_window,
            clickType="double",
            **option2
        )
    
    def _shareScreen_open(self, path : str):
        pyautogui.typewrite(path)
        pyautogui.hotkey('enter')

    def share_video(
        self, path : str,
        send_to_monitor : int = None,
        maximize : bool = True
    ):
        self._shareScreen(
            "Advanced", 
            matchOptions(
                image="%zoomto%/sharescreen_advanced_video.png",text="Video"
            )
        )
        self._shareScreen_open(
            path   
        )

        sleep(0.3)
        pyautogui.hotkey('space')

        sleep(1)
        wnd = gw.getActiveWindow()

        if send_to_monitor is not None:
            wnd.moveTo(
                screeninfo.get_monitors()[send_to_monitor].x,
                screeninfo.get_monitors()[send_to_monitor].y
            )

        if maximize:
            wnd.maximize()