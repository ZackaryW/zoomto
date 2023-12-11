import tkinter as tk
from tkinter import ttk
import pyautogui
import screeninfo
import pygetwindow as gw

class MouseCoordinateTracker:
    def __init__(self, root):
        self.root = root
        

        self.coordinate_label = tk.Label(root, text="Coordinates: 0, 0")
        self.coordinate_label.pack()

        self.create_footer()

        #displays screen size
        self.root.title(f"Mouse Coordinate Tracker ({self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()})")

        self.update_coordinates()

    def create_footer(self):
        footer = tk.Frame(self.root)
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        # Checkbox
        self.extra_option_var = tk.BooleanVar()
        tk.Checkbutton(footer, text="Extra Option", variable=self.extra_option_var).pack(side=tk.LEFT)

        # Dropdown for Monitors
        self.monitor_var = tk.StringVar()
        self.monitor_dropdown = ttk.Combobox(footer, textvariable=self.monitor_var)
        self.monitor_dropdown.pack(side=tk.LEFT)

        # Dropdown for Windows
        self.window_var = tk.StringVar()
        self.window_dropdown = ttk.Combobox(footer, textvariable=self.window_var)
        self.window_dropdown.pack(side=tk.LEFT)

        # Refresh Button
        refresh_button = tk.Button(footer, text="Refresh", command=self.refresh_options)
        refresh_button.pack(side=tk.LEFT)

        self.refresh_options()

    def refresh_options(self):
        # Update monitor options
        monitor_options = ["None"] + [f"Monitor {i+1}" for i in range(len(screeninfo.get_monitors()))]
        self.monitor_dropdown['values'] = monitor_options
        self.monitor_dropdown.set("None")

        # Update window options
        self.window_options = {w.title: w for w in gw.getAllWindows() if not w.title.startswith("<") and w.title != ""}
        self.window_dropdown['values'] = ["None"] + list(self.window_options.keys())
        self.window_var.set("None")

    def _internal_update(self):
        x, y = pyautogui.position()
        coordinate_text = f"Absolute: {x}, {y}"

        monitor_selected = self.monitor_var.get()
        window_selected = self.window_var.get()

        if monitor_selected.startswith("Monitor") and self.extra_option_var.get():
            monitor_index = int(monitor_selected.split()[1]) - 1
            monitors = screeninfo.get_monitors()
            if monitor_index < len(monitors):
                monitor = monitors[monitor_index]
                x -= monitor.x
                y -= monitor.y
            coordinate_text = f"Monitor Relative: {x}, {y}"
        elif window_selected != "None" and self.extra_option_var.get() and window_selected in self.window_options:
            window = self.window_options[window_selected]
            x -= window.left
            y -= window.top
            coordinate_text = f"Window Relative: {x}/{window.width}, {y}/{window.height}"

        self.coordinate_label.config(text=coordinate_text)

    def update_coordinates(self):
        try:
            self._internal_update()
        except: # noqa
            coordinate_text = "Error"
            self.coordinate_label.config(text=coordinate_text)
        self.root.after(100, self.update_coordinates)

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCoordinateTracker(root)
    root.mainloop()
