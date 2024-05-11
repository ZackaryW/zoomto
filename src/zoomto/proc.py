from functools import lru_cache
import time
import psutil
import win32process
import pygetwindow as gw

NON_INDEXED_WNDS = ['ZMonitorNumberIndicator', 'ZoomShadow']

@lru_cache(maxsize=3)
def get_pid_from_hwnd(hwnd):
    """ Get the process ID given the handle of a window. """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def getZoomProcesses() -> list[psutil.Process]:
    procs = []
    for proc in psutil.process_iter():
        if proc.name().lower() == "zoom.exe":
            procs.append(proc)

    return procs

def getZoomWindows()-> list[gw.Win32Window]:

    zoom_windows = []
    zoom_processes = getZoomProcesses()
    for proc in zoom_processes:
        try:
            for window in gw.getAllWindows():
                window : gw.Win32Window
                
                if get_pid_from_hwnd(window._hWnd) == proc.pid:
                    zoom_windows.append(window)
        except (gw.PyGetWindowException):
            continue
    
    return zoom_windows

_cached = None
_cached_timestamp = 0
MAX_CACHE_LIFE = 1 # in seconds

def getVisibileZoomWindows(refetch = False) -> list[gw.Win32Window]:
    global _cached
    global _cached_timestamp

    if refetch or _cached is None or (time.time() - _cached_timestamp) > MAX_CACHE_LIFE:
        zoom_windows = getZoomWindows()
        _cached = zoom_windows
        _cached_timestamp = time.time()
    else:
        zoom_windows = _cached
        
    res = []
    for w in zoom_windows:
        try:
            if w.height > 0 and w.width > 0 and w.visible and w.title not in NON_INDEXED_WNDS:
                res.append(w)
        except gw.PyGetWindowException:
            continue
        
    return res