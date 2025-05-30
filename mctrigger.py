# This script is a Python-based Minecraft triggerbot that continuously monitors a specific on-screen pixel near the crosshair, and simulates a mouse click when a certain RGB color (indicating a full attack charge) is detected, with a GUI overlay for real-time RGB feedback.

import pyautogui
import time
import threading
import tkinter as tk

# === Configuration ===
check_interval = 0.05  # Seconds
attack_delay = 0.7     # Seconds between swings
FULL_INDICATOR_RGB = (255, 255, 255)  # Replace with real value from your game

# For tracking
last_attack_time = 0
enabled = True

# === GUI Overlay ===
class DebugOverlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.attributes("-alpha", 0.6)
        self.canvas = tk.Canvas(self, width=100, height=50, bg='black', highlightthickness=0)
        self.canvas.pack()
        self.rgb_text = self.canvas.create_text(50, 15, text="", fill="white", font=("Arial", 10))

        # Crosshair mark (red box where we're watching)
        self.cross_dot = self.canvas.create_rectangle(45, 30, 55, 40, fill="red")

        screen_width, screen_height = pyautogui.size()
        self.geometry(f"+{screen_width//2 - 50}+{screen_height//2 - 25}")
        self.update_color_display((0, 0, 0))

    def update_color_display(self, rgb):
        r, g, b = rgb
        self.canvas.itemconfig(self.rgb_text, text=f"RGB: {r}, {g}, {b}")

# === Triggerbot Logic ===
def get_crosshair_pixel():
    screen_width, screen_height = pyautogui.size()
    x = screen_width // 2
    y = screen_height // 2 + 40  # Try adjusting +10 to +12, +15 etc. if it's off
    return (x, y), pyautogui.pixel(x, y)

def triggerbot_loop(overlay):
    global last_attack_time
    while True:
        if enabled:
            (x, y), current_color = get_crosshair_pixel()
            overlay.update_color_display(current_color)

            if current_color == FULL_INDICATOR_RGB:
                current_time = time.time()
                if current_time - last_attack_time >= attack_delay:
                    pyautogui.click()
                    last_attack_time = current_time
        time.sleep(check_interval)

# === Main ===
if __name__ == "__main__":
    print("Running triggerbot. Close the window to stop.")
    print("Make sure 'Attack Indicator' is set to Crosshair in Minecraft settings.")

    overlay = DebugOverlay()
    threading.Thread(target=triggerbot_loop, args=(overlay,), daemon=True).start()
    overlay.mainloop()
