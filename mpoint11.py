import ctypes
import os.path
import time
import tkinter as tk

from tkinter import ttk, scrolledtext
from pynput import keyboard

xtitle = os.path.abspath( __file__ ).split('\\')[-1]

# =====================================================
# Windows API
# =====================================================
class POINT(ctypes.Structure):
    _fields_ = [
                ("x", ctypes.c_long), 
                ("y", ctypes.c_long)
    ]

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


def get_mouse_position():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def get_pixel_color(x, y):
    hdc = user32.GetDC(None)
    color = gdi32.GetPixel(hdc, x, y)
    user32.ReleaseDC(None, hdc)

    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return r, g, b


# =====================================================
# GUI Application
# =====================================================
class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(xtitle+' JYHn')
        self.root.geometry("265x255+1637+0")
        self.root.resizable(False, False)

        self.running = False
        self.last_time = 0

        self.last_x = self.last_y = 0
        self.last_r = self.last_g = self.last_b = 0

        self.log_point = ""
        self.log_rgb = ""
        self.log_rgbhex = ""

        # ================= Labels =================
        self.pos_label = ttk.Label(
            root, text="Point:", font=("Segoe UI", 12), anchor="w"
        )
        self.pos_label.pack(padx=10, fill="x")

        self.rgb_label = ttk.Label(
            root, text="RGB:", font=("Consolas", 10), anchor="w"
        )
        self.rgb_label.pack(padx=10, fill="x")

        self.info_label = ttk.Label(
            root, 
            text=("Press [left-Shift] to copy coordinates\n"
                  "Click [RGB] to copy RGB\n"
                  "Click [RGB_H] to copy RGB_Hex"
                ),
            font=("Segoe UI", 9), anchor="w"
        )

        self.info_label.pack(padx=10, fill="x")

        # ================= Buttons =================
        btn_frame = ttk.Frame(root)
        btn_frame.pack(anchor="w", pady=2)

        ttk.Button(btn_frame, text="Start", width=6, command=self.start)\
            .pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Stop", width=6, command=self.stop)\
            .pack(side="left")

        ttk.Button(btn_frame, text="RGB", width=6, command=self.copy_rgb)\
            .pack(side="left", padx=10)
        ttk.Button(btn_frame, text="RGB_H", width=6, command=self.copy_rgbhex)\
            .pack(side="left")

        # ================= Log =================
        self.log_box = scrolledtext.ScrolledText(
            root, width=44, height=7,
            font=("Consolas", 10), state="disabled"
        )
        self.log_box.pack(padx=10, pady=3, fill="both")

        # ================= Start =================
        self.start()
        self.start_keyboard_listener()

    # =================================================
    # Logic
    # =================================================
    def start(self):
        if not self.running:
            self.running = True
            self.update_position()

    def stop(self):
        self.running = False

    def read_position(self):
        x, y = get_mouse_position()
        r, g, b = get_pixel_color(x, y)

        self.last_x, self.last_y = x, y
        self.last_r, self.last_g, self.last_b = r, g, b

    def update_position(self):
        if not self.running:
            return

        self.read_position()

        self.pos_label.config(text=f"Point:  {self.last_x}, {self.last_y}")

        hex_color = f"#{self.last_r:02X}{self.last_g:02X}{self.last_b:02X}"
        self.rgb_label.config(
            text=f"  RGB: {self.last_r},{self.last_g},{self.last_b}\n  HEX: {hex_color}"
        )

        self.root.after(50, self.update_position)

    # =================================================
    # Copy & Log
    # =================================================
    def log_current_point(self):
        if not self.running:
            return

        self.read_position() # 현재의 함수에서 delay없게 하기 위해.

        self.log_point = f"{self.last_x},{self.last_y}"
        self.log_rgb = f"({self.last_r},{self.last_g},{self.last_b})"
        self.log_rgbhex = f"#{self.last_r:02X}{self.last_g:02X}{self.last_b:02X}"

        log_text = f"{self.log_point} {self.log_rgb} {self.log_rgbhex}"

        # Clipboard (좌표 기준)
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_point)

        # Tk-safe log insert
        self.root.after(0, self._append_log, log_text)

    def _append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def copy_rgb(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_rgb)

    def copy_rgbhex(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_rgbhex)

    # =================================================
    # pynput Keyboard Listener
    # =================================================
    def start_keyboard_listener(self):
        def on_press(key):
            if key == keyboard.Key.shift_l:
                now = time.monotonic()

                if now - self.last_time >= 1.0: # cool time of shift_l key
                    self.last_time = now
                    self.log_current_point()

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()


# =====================================================
# Run
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()
