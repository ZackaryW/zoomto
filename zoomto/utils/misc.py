import win32process
import psutil
import pygetwindow as gw
import json

def get_zoom_process():

    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == "zoom.exe" and len(proc.cmdline()) >1:
                return proc

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
def get_pid_from_hwnd(hwnd):
    """ Get the process ID given the handle of a window. """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        print(f"Error: {e}")
        return None

def windowIsParent(parentWindow : gw.Window, childWindow : gw.Window, direct : bool = True):
    pidParent = get_pid_from_hwnd(parentWindow._hWnd)
    pidChild = get_pid_from_hwnd(childWindow._hWnd)

    procParent = psutil.Process(pidParent)
    procChild = psutil.Process(pidChild)

    if direct:
        return procParent in procChild.children()
    else:
        return procParent in procChild.children(recursive=True)

def load_json(filename : str):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}