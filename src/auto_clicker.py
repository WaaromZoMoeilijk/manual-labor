"""
Auto Clicker - A simple auto clicker with GUI
Features: Adjustable CPS, hotkey toggle (F6), click counter
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("300x250")
        self.root.resizable(False, False)

        # State
        self.is_running = False
        self.click_count = 0
        self.cps = 10  # clicks per second
        self.mouse_button = Button.left
        self.mouse = MouseController()
        self.click_thread = None

        # Build the GUI
        self.setup_gui()

        # Start keyboard listener for hotkey
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Auto Clicker", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # CPS Slider
        cps_frame = ttk.Frame(main_frame)
        cps_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cps_frame, text="Clicks per second:").pack(side=tk.LEFT)
        self.cps_label = ttk.Label(cps_frame, text=str(self.cps))
        self.cps_label.pack(side=tk.RIGHT)

        self.cps_slider = ttk.Scale(
            main_frame,
            from_=1,
            to=50,
            value=self.cps,
            orient=tk.HORIZONTAL,
            command=self.update_cps
        )
        self.cps_slider.pack(fill=tk.X, pady=(0, 10))

        # Mouse button selection
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Label(button_frame, text="Mouse button:").pack(side=tk.LEFT)
        self.button_var = tk.StringVar(value="Left")
        button_combo = ttk.Combobox(
            button_frame,
            textvariable=self.button_var,
            values=["Left", "Right"],
            state="readonly",
            width=10
        )
        button_combo.pack(side=tk.RIGHT)
        button_combo.bind("<<ComboboxSelected>>", self.update_button)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Status: Stopped",
            font=("Arial", 12),
            foreground="red"
        )
        self.status_label.pack(pady=10)

        # Click counter
        self.counter_label = ttk.Label(
            main_frame,
            text="Clicks: 0",
            font=("Arial", 10)
        )
        self.counter_label.pack()

        # Start/Stop button
        self.toggle_button = ttk.Button(
            main_frame,
            text="Start (F6)",
            command=self.toggle_clicking
        )
        self.toggle_button.pack(pady=10, ipadx=20, ipady=5)

        # Hotkey hint
        hint_label = ttk.Label(
            main_frame,
            text="Press F6 to toggle on/off",
            font=("Arial", 8),
            foreground="gray"
        )
        hint_label.pack()

    def update_cps(self, value):
        self.cps = int(float(value))
        self.cps_label.config(text=str(self.cps))

    def update_button(self, event=None):
        if self.button_var.get() == "Left":
            self.mouse_button = Button.left
        else:
            self.mouse_button = Button.right

    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        self.is_running = True
        self.status_label.config(text="Status: Running", foreground="green")
        self.toggle_button.config(text="Stop (F6)")

        # Start clicking in a separate thread
        self.click_thread = threading.Thread(target=self.clicking_loop, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="Status: Stopped", foreground="red")
        self.toggle_button.config(text="Start (F6)")

    def clicking_loop(self):
        while self.is_running:
            self.mouse.click(self.mouse_button)
            self.click_count += 1

            # Update counter in main thread
            self.root.after(0, self.update_counter)

            # Wait based on CPS
            time.sleep(1 / self.cps)

    def update_counter(self):
        self.counter_label.config(text=f"Clicks: {self.click_count}")

    def on_key_press(self, key):
        if key == Key.f6:
            # Schedule toggle in main thread
            self.root.after(0, self.toggle_clicking)

    def on_close(self):
        self.is_running = False
        self.keyboard_listener.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
