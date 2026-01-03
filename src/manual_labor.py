"""
Manual Labor - A feature-rich auto clicker with GUI
Features: Adjustable CPS, multiple click modes, hotkeys, themes, and more
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import json
import os
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener, KeyCode

# Settings file path
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".manual_labor_settings.json")

# Available hotkeys
HOTKEY_OPTIONS = {
    "F6": Key.f6,
    "F7": Key.f7,
    "F8": Key.f8,
    "F9": Key.f9,
    "F10": Key.f10,
}


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Labor")
        self.root.geometry("350x580")
        self.root.resizable(False, False)

        # State
        self.is_running = False
        self.click_count = 0
        self.cps = 10
        self.mouse_button = Button.left
        self.mouse = MouseController()
        self.click_thread = None

        # Feature settings
        self.random_variation = 15  # ±15% timing variation
        self.click_limit = 0  # 0 = unlimited
        self.hotkey = Key.f6
        self.hotkey_name = "F6"
        self.use_fixed_position = False
        self.fixed_x = 0
        self.fixed_y = 0
        self.double_click = False
        self.start_delay = 0  # seconds
        self.hold_mode = False
        self.is_holding = False
        self.dark_mode = False
        self.click_sound = False

        # Load saved settings
        self.load_settings()

        # Apply theme
        self.setup_styles()

        # Build the GUI
        self.setup_gui()

        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # System tray (minimize)
        self.root.bind("<Unmap>", self.on_minimize)

    def setup_styles(self):
        """Setup ttk styles for theming"""
        self.style = ttk.Style()

        if self.dark_mode:
            self.root.configure(bg="#2b2b2b")
            self.style.configure("TFrame", background="#2b2b2b")
            self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("TButton", background="#404040")
            self.style.configure("TCheckbutton", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("TScale", background="#2b2b2b")
            self.style.configure("Header.TLabel", background="#2b2b2b", foreground="#ffffff", font=("Arial", 16, "bold"))
            self.style.configure("Status.TLabel", background="#2b2b2b", font=("Arial", 11))
        else:
            self.root.configure(bg="#f0f0f0")
            self.style.configure("TFrame", background="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            self.style.configure("TCheckbutton", background="#f0f0f0")
            self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
            self.style.configure("Status.TLabel", font=("Arial", 11))

    def setup_gui(self):
        """Build the GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Manual Labor", style="Header.TLabel").pack(pady=(0, 10))

        # === CPS Section ===
        cps_frame = ttk.LabelFrame(main_frame, text="Speed", padding="5")
        cps_frame.pack(fill=tk.X, pady=5)

        cps_row = ttk.Frame(cps_frame)
        cps_row.pack(fill=tk.X)
        ttk.Label(cps_row, text="Clicks per second:").pack(side=tk.LEFT)
        self.cps_label = ttk.Label(cps_row, text=str(self.cps))
        self.cps_label.pack(side=tk.RIGHT)

        self.cps_slider = ttk.Scale(cps_frame, from_=1, to=50, value=self.cps,
                                     orient=tk.HORIZONTAL, command=self.update_cps)
        self.cps_slider.pack(fill=tk.X)

        # Random variation
        var_row = ttk.Frame(cps_frame)
        var_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(var_row, text="Timing variation ±%:").pack(side=tk.LEFT)
        self.variation_label = ttk.Label(var_row, text=str(self.random_variation))
        self.variation_label.pack(side=tk.RIGHT)

        self.variation_slider = ttk.Scale(cps_frame, from_=0, to=30, value=self.random_variation,
                                          orient=tk.HORIZONTAL, command=self.update_variation)
        self.variation_slider.pack(fill=tk.X)

        # === Click Options ===
        options_frame = ttk.LabelFrame(main_frame, text="Click Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)

        # Mouse button
        btn_row = ttk.Frame(options_frame)
        btn_row.pack(fill=tk.X, pady=2)
        ttk.Label(btn_row, text="Mouse button:").pack(side=tk.LEFT)
        self.button_var = tk.StringVar(value="Left" if self.mouse_button == Button.left else "Right")
        btn_combo = ttk.Combobox(btn_row, textvariable=self.button_var,
                                  values=["Left", "Right", "Middle"], state="readonly", width=10)
        btn_combo.pack(side=tk.RIGHT)
        btn_combo.bind("<<ComboboxSelected>>", self.update_button)

        # Double click checkbox
        self.double_var = tk.BooleanVar(value=self.double_click)
        ttk.Checkbutton(options_frame, text="Double click", variable=self.double_var,
                        command=self.update_double_click).pack(anchor=tk.W)

        # Click limit
        limit_row = ttk.Frame(options_frame)
        limit_row.pack(fill=tk.X, pady=2)
        ttk.Label(limit_row, text="Click limit (0=unlimited):").pack(side=tk.LEFT)
        self.limit_var = tk.StringVar(value=str(self.click_limit))
        limit_entry = ttk.Entry(limit_row, textvariable=self.limit_var, width=8)
        limit_entry.pack(side=tk.RIGHT)
        limit_entry.bind("<FocusOut>", self.update_click_limit)

        # === Position ===
        pos_frame = ttk.LabelFrame(main_frame, text="Position", padding="5")
        pos_frame.pack(fill=tk.X, pady=5)

        self.pos_var = tk.BooleanVar(value=self.use_fixed_position)
        ttk.Checkbutton(pos_frame, text="Use fixed position", variable=self.pos_var,
                        command=self.toggle_fixed_position).pack(anchor=tk.W)

        pos_row = ttk.Frame(pos_frame)
        pos_row.pack(fill=tk.X, pady=2)
        ttk.Label(pos_row, text="X:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar(value=str(self.fixed_x))
        self.x_entry = ttk.Entry(pos_row, textvariable=self.x_var, width=6, state="disabled")
        self.x_entry.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(pos_row, text="Y:").pack(side=tk.LEFT)
        self.y_var = tk.StringVar(value=str(self.fixed_y))
        self.y_entry = ttk.Entry(pos_row, textvariable=self.y_var, width=6, state="disabled")
        self.y_entry.pack(side=tk.LEFT)

        self.capture_btn = ttk.Button(pos_row, text="Capture", command=self.capture_position, state="disabled")
        self.capture_btn.pack(side=tk.RIGHT)

        # === Hotkey & Delay ===
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_frame.pack(fill=tk.X, pady=5)

        # Hotkey selection
        hk_row = ttk.Frame(control_frame)
        hk_row.pack(fill=tk.X, pady=2)
        ttk.Label(hk_row, text="Hotkey:").pack(side=tk.LEFT)
        self.hotkey_var = tk.StringVar(value=self.hotkey_name)
        hk_combo = ttk.Combobox(hk_row, textvariable=self.hotkey_var,
                                 values=list(HOTKEY_OPTIONS.keys()), state="readonly", width=10)
        hk_combo.pack(side=tk.RIGHT)
        hk_combo.bind("<<ComboboxSelected>>", self.update_hotkey)

        # Hold mode
        self.hold_var = tk.BooleanVar(value=self.hold_mode)
        ttk.Checkbutton(control_frame, text="Hold mode (hold hotkey to click)",
                        variable=self.hold_var, command=self.update_hold_mode).pack(anchor=tk.W)

        # Start delay
        delay_row = ttk.Frame(control_frame)
        delay_row.pack(fill=tk.X, pady=2)
        ttk.Label(delay_row, text="Start delay (seconds):").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value=str(self.start_delay))
        delay_entry = ttk.Entry(delay_row, textvariable=self.delay_var, width=6)
        delay_entry.pack(side=tk.RIGHT)
        delay_entry.bind("<FocusOut>", self.update_delay)

        # === Extras ===
        extras_frame = ttk.LabelFrame(main_frame, text="Extras", padding="5")
        extras_frame.pack(fill=tk.X, pady=5)

        self.sound_var = tk.BooleanVar(value=self.click_sound)
        ttk.Checkbutton(extras_frame, text="Click sound", variable=self.sound_var,
                        command=self.update_sound).pack(anchor=tk.W)

        self.dark_var = tk.BooleanVar(value=self.dark_mode)
        ttk.Checkbutton(extras_frame, text="Dark mode", variable=self.dark_var,
                        command=self.toggle_dark_mode).pack(anchor=tk.W)

        # === Status ===
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)

        self.status_label = ttk.Label(status_frame, text="Status: Stopped",
                                       style="Status.TLabel", foreground="red")
        self.status_label.pack()

        self.counter_label = ttk.Label(status_frame, text="Clicks: 0")
        self.counter_label.pack()

        # Start/Stop button
        self.toggle_button = ttk.Button(main_frame, text=f"Start ({self.hotkey_name})",
                                         command=self.toggle_clicking)
        self.toggle_button.pack(pady=5, ipadx=20, ipady=5)

        # Save button
        ttk.Button(main_frame, text="Save Settings", command=self.save_settings).pack(pady=2)

        # Hint
        ttk.Label(main_frame, text=f"Press {self.hotkey_name} to toggle",
                  font=("Arial", 8), foreground="gray").pack()

    def update_cps(self, value):
        self.cps = int(float(value))
        self.cps_label.config(text=str(self.cps))

    def update_variation(self, value):
        self.random_variation = int(float(value))
        self.variation_label.config(text=str(self.random_variation))

    def update_button(self, event=None):
        btn = self.button_var.get()
        if btn == "Left":
            self.mouse_button = Button.left
        elif btn == "Right":
            self.mouse_button = Button.right
        else:
            self.mouse_button = Button.middle

    def update_double_click(self):
        self.double_click = self.double_var.get()

    def update_click_limit(self, event=None):
        try:
            self.click_limit = int(self.limit_var.get())
        except ValueError:
            self.click_limit = 0
            self.limit_var.set("0")

    def toggle_fixed_position(self):
        self.use_fixed_position = self.pos_var.get()
        state = "normal" if self.use_fixed_position else "disabled"
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)
        self.capture_btn.config(state=state)

    def capture_position(self):
        """Capture current mouse position after 2 seconds"""
        self.capture_btn.config(text="Move mouse...")
        self.root.after(2000, self._do_capture)

    def _do_capture(self):
        pos = self.mouse.position
        self.fixed_x = int(pos[0])
        self.fixed_y = int(pos[1])
        self.x_var.set(str(self.fixed_x))
        self.y_var.set(str(self.fixed_y))
        self.capture_btn.config(text="Capture")

    def update_hotkey(self, event=None):
        self.hotkey_name = self.hotkey_var.get()
        self.hotkey = HOTKEY_OPTIONS[self.hotkey_name]
        self.toggle_button.config(text=f"Start ({self.hotkey_name})")

    def update_hold_mode(self):
        self.hold_mode = self.hold_var.get()

    def update_delay(self, event=None):
        try:
            self.start_delay = float(self.delay_var.get())
        except ValueError:
            self.start_delay = 0
            self.delay_var.set("0")

    def update_sound(self):
        self.click_sound = self.sound_var.get()

    def toggle_dark_mode(self):
        self.dark_mode = self.dark_var.get()
        self.setup_styles()
        # Rebuild GUI to apply theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_gui()

    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        """Start the auto clicker with optional delay"""
        if self.start_delay > 0:
            self.status_label.config(text=f"Starting in {self.start_delay}s...", foreground="orange")
            self.root.after(int(self.start_delay * 1000), self._do_start)
        else:
            self._do_start()

    def _do_start(self):
        self.is_running = True
        self.click_count = 0
        self.status_label.config(text="Status: Running", foreground="green")
        self.toggle_button.config(text=f"Stop ({self.hotkey_name})")
        self.click_thread = threading.Thread(target=self.clicking_loop, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.status_label.config(text="Status: Stopped", foreground="red")
        self.toggle_button.config(text=f"Start ({self.hotkey_name})")

    def clicking_loop(self):
        """Main clicking loop with all features"""
        while self.is_running:
            # Check click limit
            if self.click_limit > 0 and self.click_count >= self.click_limit:
                self.root.after(0, self.stop_clicking)
                break

            # Move to fixed position if enabled
            if self.use_fixed_position:
                try:
                    self.fixed_x = int(self.x_var.get())
                    self.fixed_y = int(self.y_var.get())
                    self.mouse.position = (self.fixed_x, self.fixed_y)
                except ValueError:
                    pass

            # Perform click(s)
            clicks = 2 if self.double_click else 1
            for _ in range(clicks):
                self.mouse.click(self.mouse_button)

            self.click_count += 1

            # Play sound if enabled
            if self.click_sound:
                self.root.after(0, lambda: self.root.bell())

            # Update counter
            self.root.after(0, self.update_counter)

            # Calculate delay with random variation
            base_delay = 1 / self.cps
            if self.random_variation > 0:
                variation = base_delay * (self.random_variation / 100)
                delay = base_delay + random.uniform(-variation, variation)
                delay = max(0.001, delay)  # Ensure positive delay
            else:
                delay = base_delay

            time.sleep(delay)

    def update_counter(self):
        self.counter_label.config(text=f"Clicks: {self.click_count}")

    def on_key_press(self, key):
        if key == self.hotkey:
            if self.hold_mode:
                if not self.is_holding:
                    self.is_holding = True
                    self.root.after(0, self.start_clicking)
            else:
                self.root.after(0, self.toggle_clicking)

    def on_key_release(self, key):
        if key == self.hotkey and self.hold_mode:
            self.is_holding = False
            self.root.after(0, self.stop_clicking)

    def on_minimize(self, event):
        """Handle minimize to tray"""
        if self.root.state() == 'iconic':
            # Window minimized - could add system tray icon here
            pass

    def save_settings(self):
        """Save settings to file"""
        settings = {
            "cps": self.cps,
            "random_variation": self.random_variation,
            "mouse_button": self.button_var.get(),
            "double_click": self.double_click,
            "click_limit": self.click_limit,
            "use_fixed_position": self.use_fixed_position,
            "fixed_x": self.fixed_x,
            "fixed_y": self.fixed_y,
            "hotkey": self.hotkey_name,
            "hold_mode": self.hold_mode,
            "start_delay": self.start_delay,
            "click_sound": self.click_sound,
            "dark_mode": self.dark_mode,
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)
            self.status_label.config(text="Settings saved!", foreground="blue")
            self.root.after(2000, lambda: self.status_label.config(
                text="Status: Stopped", foreground="red"))
        except Exception as e:
            self.status_label.config(text=f"Save failed: {e}", foreground="red")

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                self.cps = settings.get("cps", 10)
                self.random_variation = settings.get("random_variation", 15)
                btn = settings.get("mouse_button", "Left")
                if btn == "Left":
                    self.mouse_button = Button.left
                elif btn == "Right":
                    self.mouse_button = Button.right
                else:
                    self.mouse_button = Button.middle
                self.double_click = settings.get("double_click", False)
                self.click_limit = settings.get("click_limit", 0)
                self.use_fixed_position = settings.get("use_fixed_position", False)
                self.fixed_x = settings.get("fixed_x", 0)
                self.fixed_y = settings.get("fixed_y", 0)
                self.hotkey_name = settings.get("hotkey", "F6")
                self.hotkey = HOTKEY_OPTIONS.get(self.hotkey_name, Key.f6)
                self.hold_mode = settings.get("hold_mode", False)
                self.start_delay = settings.get("start_delay", 0)
                self.click_sound = settings.get("click_sound", False)
                self.dark_mode = settings.get("dark_mode", False)
        except Exception:
            pass  # Use defaults if load fails

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
