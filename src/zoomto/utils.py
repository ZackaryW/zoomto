from functools import cache
import time
import typing
import screeninfo
import pygetwindow as gw
import psutil
import win32process
from datetime import datetime, timedelta

@cache
def get_primary_monitor():
    """
    Returns the primary monitor object from the list of all monitors.

    This function iterates over the list of monitors obtained from the `screeninfo.get_monitors()` function and checks if each monitor is the primary monitor. If a primary monitor is found, it is returned. If no primary monitor is found, a `ValueError` is raised with the message "No primary monitor found".

    Returns:
        screeninfo.Monitor: The primary monitor object.

    Raises:
        ValueError: If no primary monitor is found.
    """
    for monitor in screeninfo.get_monitors():
        if monitor.is_primary:
            return monitor

    raise ValueError("No primary monitor found")

@cache
def get_zoom_proc() -> typing.List[psutil.Process]:
    procs = []
    for proc in psutil.process_iter():
        if proc.name().lower() == "zoom.exe":
            procs.append(proc)

    return procs

def get_pid_from_hwnd(hwnd):
    """ Get the process ID given the handle of a window. """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        print(f"Error: {e}")
        return None

def window_is_visible(window: gw.Win32Window) -> bool:
    if window.height <= 0:
        return False
    if window.width <= 0:
        return False
    if window.top < 0:
        return False
    if window.left < 0:
        return False
    return True

SPECIAL_WNDS = ['ZMonitorNumberIndicator', 'ZoomShadow']

_last_fetch_timestamp = 0

@cache
def _internal_get_zoom_windows(visible_only : bool = True, exclude_special : bool = True):
    zoom_windows = []
    zoom_processes = get_zoom_proc()
    for proc in zoom_processes:
        try:
            for window in gw.getAllWindows():
                window : gw.Win32Window
                
                if visible_only and not window_is_visible(window):
                    continue

                if exclude_special and window.title in SPECIAL_WNDS:
                    continue

                if get_pid_from_hwnd(window._hWnd) == proc.pid:
                    zoom_windows.append(window)
        except (gw.PyGetWindowException):
            continue
    
    return zoom_windows

def get_zoom_windows(visible_only : bool = True, exclude_special : bool = True, clear_cache : bool = False) -> typing.List[gw.Win32Window]:        

    if not clear_cache:
        global _last_fetch_timestamp
        # if within the same second
        curr = time.time()
        if curr - _last_fetch_timestamp > 1:
            _internal_get_zoom_windows.cache_clear()
    else:
        _internal_get_zoom_windows.cache_clear()

    return _internal_get_zoom_windows(visible_only, exclude_special)


def window_in_monitor(window: gw.Win32Window, monitor: screeninfo.Monitor) -> bool:
    if window.left < monitor.x:
        return False
    if window.top < monitor.y:
        return False
    if window.right > monitor.x + monitor.width:
        return False
    if window.bottom > monitor.y + monitor.height:
        return False
    return True

def get_window_current_monitor(window : gw.Win32Window) -> screeninfo.Monitor:
    for monitor in screeninfo.get_monitors():
        if window_in_monitor(window, monitor):
            return monitor
        
    raise ValueError("No monitor found")

def move_window_to_monitor(window: gw.Win32Window, monitor: screeninfo.Monitor) -> bool:
    """
    Move a window to a specified monitor.

    Args:
        window (gw.Win32Window): The window to be moved.
        monitor (screeninfo.Monitor): The target monitor.

    Returns:
        bool: True if the window was moved, False if it was already on the target monitor.
    """
    if window_in_monitor(window, monitor):
        return False
    
    # Calculate the relative coordinates of current monitor
    current_monitor = get_window_current_monitor(window)
    rel_x = window.left - current_monitor.x
    rel_y = window.top - current_monitor.y

    # Calculate distance between the two monitors
    dx = monitor.x - current_monitor.x
    dy = monitor.y - current_monitor.y

    # Move the window to the new monitor
    new_x = monitor.x + rel_x
    new_y = monitor.y + rel_y

    window.move(new_x+dx, new_y+dy)
    return True

def activate_wnd(wnd : gw.Win32Window):
    """
    Activate a window.
    """
    try:
        if wnd.isActive:
            return
        
        wnd.activate()
    except Exception:
        pass

def parse_time(time_str : str):
    # Try parsing as pure number (seconds)
    if time_str.isdigit():
        return int(time_str)
    
    # Try parsing as time format
    time_formats = [
        "%I:%M%p",  # 10:25am
        "%I%M%p",   # 1035pm
        "%H:%M",    # 10:25 (24-hour)
        "%H%M"      # 2235 (24-hour)
    ]
    
    for fmt in time_formats:
        try:
            parsed_time = datetime.strptime(time_str.lower(), fmt)
            now = datetime.now()
            target_time = now.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0, microsecond=0)
            
            if target_time <= now:
                target_time += timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            return int(wait_seconds)
        except ValueError:
            continue
    
    raise ValueError(f"Invalid time format: {time_str}")

def wait_timer(string :str):
    """
    accepted strings:
    pure numbers (e.g 1000 / 5333) in seconds
    time formats (e.g 10:25am/ 1035pm)
    or 24 hour formats (e.g 10:25)
    """
    wait_seconds = parse_time(string)
    print(f"Waiting for {wait_seconds} seconds till {datetime.now() + timedelta(seconds=wait_seconds)}")
    time.sleep(wait_seconds)
