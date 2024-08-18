
from time import sleep
from zoomto.utils import activate_wnd, get_primary_monitor, get_zoom_windows, move_window_to_monitor
import pyautogui as pg
pg.FAILSAFE = False
ADVANCED_POI = [527, 44]

VIDEO_FILE_POI = [398, 355]

SCREENS_POI = [272, 45]

SCREEN_1_POI = [140,228]


def rel_wnd_coord(wnd, xy):
    return [wnd.left + xy[0], wnd.top + xy[1]]

def detect_share_screen_dialog():
    for window in get_zoom_windows():
        if window.title.startswith("Select a window"):
            return True
    return False

def get_main_meeting_window():
    for window in get_zoom_windows():
        if window.title.startswith("Zoom Meeting Participant ID: "):
            return window

def get_share_screen_dialog(dialog_to_primary = True):
    if dialog_to_primary:
        primary = get_primary_monitor()

    if detect_share_screen_dialog():
        for window in get_zoom_windows():
            if window.title.startswith("Select a window"):
                if dialog_to_primary: 
                    move_window_to_monitor(window, primary)
                return window
    
    wnd = get_main_meeting_window()
    activate_wnd(wnd)

    with pg.hold("alt"):
        pg.keyDown("s")

    sleep(0.5)

    for window in get_zoom_windows(clear_cache=True):
        if window.title.startswith("Select a window"):
            if  dialog_to_primary: 
                move_window_to_monitor(window, primary)
            return window
        
def share_screen(screen = 1):
    #TODO - 
    raise NotImplementedError

def share_video(video_path : str, start_playing = True):
    wnd = get_share_screen_dialog()

    activate_wnd(wnd)
    pg.click(*rel_wnd_coord(wnd, ADVANCED_POI))    
    sleep(0.1)
    pg.doubleClick(*rel_wnd_coord(wnd, VIDEO_FILE_POI))
    sleep(0.1)
    pg.typewrite(video_path)
    sleep(0.1)
    pg.press("enter")

    
    if start_playing:
        mwnd = get_main_meeting_window()
        activate_wnd(mwnd)
        sleep(0.1)
        # 
        pg.moveTo(mwnd.left, mwnd.height-90, duration=0.3)
        pg.click()
        pg.press("space")


