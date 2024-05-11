import os
from time import sleep

from pygetwindow._pygetwindow_win import Win32Window
from zoomto.proc import getVisibileZoomWindows, getZoomWindows
import pyautogui as pg
import pygetwindow as gw

from zoomto.utils import activateWnd, sendWindowToMonitor

staticFolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
currentlyServing : str = None

def getMeetingWnd(skipVFW = False):
    frameWnd= None
    for wnd in getVisibileZoomWindows(refetch=True):
        if wnd.title.lower().startswith("zoom meeting"):
            return wnd
        if wnd.title == "VideoFrameWnd":
            frameWnd = wnd

    if frameWnd and not skipVFW:
        # move to the bottom right of the window
        pg.moveTo(wnd.center, duration=0.2)
        sleep(0.2)
        pg.click(os.path.join(staticFolder, "meeting_expand.png"))
        return getMeetingWnd(True)


def getSelectAWnd(refetch = False) -> Win32Window:
    for wnd in getVisibileZoomWindows(refetch=refetch):
        if wnd.title.lower().startswith("select a window or"):
            if wnd.title.endswith("share"):
                return wnd
            
def closeJoinAudio():
    for wnd in getZoomWindows():
        if wnd.title.lower() == "join audio":
            wnd.close()
    
def getZoomCtrlWnd() -> Win32Window:
    for wnd in getVisibileZoomWindows():
        if "screen sharing meeting controls" in wnd.title.lower():
            return wnd

def stopExistingShare():
    if (zoomctrl := getZoomCtrlWnd()):
        global currentlyServing
        currentlyServing = None

        activateWnd(zoomctrl)
        with pg.hold("alt"):
            pg.press("s")

def shareVideo(address : str, monitor = 0):
    closeJoinAudio()

    stopExistingShare()
        

    selectAWnd = getSelectAWnd()

    if not selectAWnd:
        meetingWnd = getMeetingWnd()
        
        sleep(0.5)
        while True:
            activateWnd(meetingWnd)
            with pg.hold("alt"):
                pg.press("s")
            sleep(0.3)
            selectAWnd = getSelectAWnd()
            if selectAWnd:
                break

    activateWnd(selectAWnd)
    pg.doubleClick(selectAWnd.topleft[0] + selectAWnd.width*3/10, selectAWnd.topleft[1] +50)
    pg.doubleClick(selectAWnd.topleft[0]+ selectAWnd.width/8, selectAWnd.centery)
    sleep(0.1)
    # get open wnd
    try:
        gw.getWindowsWithTitle("Open")[0].activate()
    except: #noqa
        pass
    pg.typewrite(address)
    pg.press("enter")

    # get active wnd
    sleep(1)
    global currentlyServing
    currentlyServing = address
    # get the wnd with filename
    active = gw.getWindowsWithTitle(os.path.basename(address))[0]
    sendWindowToMonitor(active, monitor)
    active.maximize()

