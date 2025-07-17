import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import sys
from PIL import Image, ImageTk

def resource_path(relative_path):
    """ Get absolute path to resource"""
    try:
        # PyInstaller creates a temp folder and stores the path in `sys._MEIPASS`
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./resources")

    return os.path.join(base_path, relative_path)

class EyeRestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EyeRest")

        vcmd_work = (self.root.register(self.validate_numeric_input), '%P', 6)
        vcmd_break = (self.root.register(self.validate_numeric_input), '%P', 4)

        original_image = Image.open(resource_path("escape.png"))  # Load the image
        resized_image = original_image.resize((100, 100), Image.LANCZOS)  # Resize to 100x100 pixels
        self.icon_image = ImageTk.PhotoImage(resized_image)  # Convert to PhotoImage

        # set window size
        self.window_width = 500
        self.window_height = 300

        # center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        # make frame for work interval
        self.work_frame = tk.Frame(root)
        self.work_frame.pack(pady=10)
        
        # make label and entry for work interval
        self.work_label = tk.Label(self.work_frame, text="Work Interval:")
        self.work_label.pack(side=tk.LEFT)
        
        self.work_value = tk.StringVar(value="20")  # Default value
        self.work_entry = tk.Entry(self.work_frame, textvariable=self.work_value, validate="key", validatecommand=vcmd_work)
        self.work_entry.pack(side=tk.LEFT)
        
        # create dropdown for work units
        self.work_unit = tk.StringVar(value="minutes")  # Default unit
        self.work_unit_button = tk.Button(self.work_frame, text=self.work_unit.get(), command=self.toggle_work_unit_menu)
        self.work_unit_button.pack(side=tk.LEFT)
        
        self.work_unit_menu = tk.Menu(root, tearoff=0)
        self.work_unit_menu.add_command(label="minutes", command=lambda: self.set_work_unit("minutes"))
        self.work_unit_menu.add_command(label="seconds", command=lambda: self.set_work_unit("seconds"))

        # For preview of countdown
        self.work_value.trace_add("write", lambda *args: self.update_main_countdown_preview())
        self.work_unit.trace_add("write", lambda *args: self.update_main_countdown_preview())

        # make frame for break interval
        self.break_frame = tk.Frame(root)
        self.break_frame.pack(pady=10)

        # make label and entry for break interval
        self.break_label = tk.Label(self.break_frame, text="Break Duration:")
        self.break_label.pack(side=tk.LEFT)
        
        self.break_value = tk.StringVar(value="20")  # Default value
        self.break_entry = tk.Entry(self.break_frame, textvariable=self.break_value, validate="key", validatecommand=vcmd_break)
        self.break_entry.pack(side=tk.LEFT)

        self.work_value.trace_add("write", lambda *args: self.validate_inputs())
        self.break_value.trace_add("write", lambda *args: self.validate_inputs())
        
        # dropdown for break units
        self.break_unit = tk.StringVar(value="seconds")  # Default unit
        self.break_unit_button = tk.Button(self.break_frame, text=self.break_unit.get(), command=self.toggle_break_unit_menu)
        self.break_unit_button.pack(side=tk.LEFT)
        
        self.break_unit_menu = tk.Menu(root, tearoff=0)
        self.break_unit_menu.add_command(label="minutes", command=lambda: self.set_break_unit("minutes"))
        self.break_unit_menu.add_command(label="seconds", command=lambda: self.set_break_unit("seconds"))

        # Countdown
        self.main_countdown = tk.Label(root, text="00:20:00", font=("Arial", 24), fg="gray")
        self.main_countdown.pack(pady=10)

        # start/stop features
        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.error_label = tk.Label(root, text="", fg="red", font=("Arial", 10))
        self.error_label.pack(pady=(5, 10))  # Add some padding for spacing        

        self.running = False
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.notif_stopped_event = threading.Event()

        # Bind close event to cleanup func
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_work_unit_menu(self):
        self.work_unit_menu.post(self.work_unit_button.winfo_rootx(), self.work_unit_button.winfo_rooty() + self.work_unit_button.winfo_height())

    def set_work_unit(self, unit):
        self.work_unit.set(unit)
        self.work_unit_button.config(text=unit)
        self.validate_inputs()

    def toggle_break_unit_menu(self):
        self.break_unit_menu.post(self.break_unit_button.winfo_rootx(), self.break_unit_button.winfo_rooty() + self.break_unit_button.winfo_height())

    def set_break_unit(self, unit):
        self.break_unit.set(unit)
        self.break_unit_button.config(text=unit)
        self.validate_inputs()

    def update_main_countdown_preview(self):
        if self.running:
            return  # Don’t update preview while timer is running

        value = self.work_value.get()
        unit = self.work_unit.get()

        if not value.isdigit():
            self.main_countdown.config(text="Invalid", fg="red")
            return

        seconds = int(value)
        if unit == "minutes":
            seconds *= 60

        # Clamp to safe display limit
        seconds = min(seconds, 359999)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        formatted = f"{hours:02}:{minutes:02}:{secs:02}"
        self.main_countdown.config(text=formatted, fg="gray")

    def validate_numeric_input(self, new_value, max_length):
        if new_value == "":
            return True  # Allow backspace
        
        if new_value.isdigit() and len(new_value) <= int(max_length):
            if new_value == "0" or new_value.startswith("0"):
                return False  # Disallow leading zeros like '01', '0001'
            return True
        
        return False
    
    def validate_inputs(self):
        error_messages = []
        
        # Validate work interval
        try:
            work_value = int(self.work_value.get())
            if work_value <= 0:
                error_messages.append("Work interval must be positive.")
            elif work_value < 5 and self.work_unit.get() == "seconds":
                error_messages.append("Work interval cannot be less than 5 seconds.")
            elif work_value > 999999:
                error_messages.append("Work interval too large.")
        except ValueError:
            error_messages.append("Work interval must be a whole number.")
            
        # Validate break duration
        try:
            break_value = int(self.break_value.get())
            if break_value <= 0:
                error_messages.append("Break duration must be positive.")
            elif break_value < 5 and self.break_unit.get() == "seconds":
                error_messages.append("Break duration cannot be less than 5 seconds.")
            elif break_value > 166 and self.break_unit.get() == "minutes":
                error_messages.append("Break duration too large. Maximum break length is 166 minutes (9999 s).")
        except ValueError:
            error_messages.append("Break duration must be a whole number.")
            
        # Update error label
        if error_messages:
            self.error_label.config(text="; ".join(error_messages))
            return False
        else:
            self.error_label.config(text="")
            return True


    # Note: all return statements in start_timer signify failure to start timer. User will be re-prompted for new input
    def start_timer(self): 
        if self.running:
            return
        if not self.validate_inputs():
            return
        
        try:
            # Get and validate values
            work_value = int(self.work_value.get())
            work_unit = self.work_unit.get()
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid work interval values. (Whole numbers only)")
            return
        
        try: # Convert to seconds and ensure positivity of number
            if work_unit == "minutes":
                self.work_interval = work_value * 60
            else:
                self.work_interval = work_value
            
            if self.work_interval <= 0:
                raise ValueError("Work interval must be positive.")
            
            if self.work_interval < 5:
                raise ValueError("Work interval cannot be less than 5 seconds.")
            
            self.work_interval = min(self.work_interval, 359999) # Clamp

        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return
        
        try:
            # Get and validate break values
            break_value = int(self.break_value.get())
            break_unit = self.break_unit.get()
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid break duration values. (Whole numbers only)")
            return

        try:
            # Convert seconds and check positivity of break value
            if break_unit == "minutes":
                self.break_duration = break_value * 60
            else:
                self.break_duration = break_value
            
            if self.break_duration <= 0:
                raise ValueError("Break duration must be positive.")
            
            if self.break_duration < 5:
                raise ValueError("Break duration cannot be less than 5 seconds.")
            
            self.break_duration = min(self.work_interval, 9999) # Clamp

        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        # Continue with starting the timer
        self.running = True
        self.stop_event.clear()
        self.notif_stopped_event.clear()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()

    def stop_timer(self):
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        self.notif_stopped_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Kill notification window if it exists
        if hasattr(self, 'top') and self.top.winfo_exists():
            self.top.destroy()

        # Hard reset the thread
        if self.timer_thread is not None:
            join_start_time = time.time()
            while self.timer_thread.is_alive():
                self.timer_thread.join(timeout=0.1) # Bleed timer
                # Break the loop after a certain timeout to avoid infinite loop
                if time.time() - join_start_time > 0.15:  # Short timeout for safety buffer to clear thread
                    break
            self.timer_thread = None
        
        # Reset countdown
        self.root.after(0, self.reset_countdown)
        self.root.after(0, lambda: self.main_countdown.config(fg='gray'))

    def on_closing(self):
        self.stop_timer()  # stop timer if running

        self.root.after(0, self.root.destroy)  # close the main window and exit

    def escape_notification_window(self):
        if hasattr(self, 'top') and self.top.winfo_exists():
            self.top.destroy()
            self.notif_stopped_event.set()

    def reset_countdown(self):
        try:
            work_value = int(self.work_value.get())
            work_unit = self.work_unit.get()

            # Convert to seconds
            if work_unit == "minutes":
                total_seconds = work_value * 60
            else:
                total_seconds = work_value
            
            # Clamp to zero if invalid
            if total_seconds < 0:
                total_seconds = 0

        except ValueError:
            # Fallback to zero if invalid input
            total_seconds = 0
        
        total_seconds = min(total_seconds, 359999)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        preview_text = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.main_countdown.config(text=preview_text, fg='gray')

            
    def run_timer(self):
        while self.running:
            if not self.running or self.stop_event.is_set():
                break
            
            # Work Interval
            work_time_remaining = self.work_interval
            start_time = time.time()
            while self.running and work_time_remaining > 0:
                time.sleep(min(0.05, work_time_remaining))  # Update every 0.05 seconds
                elapsed = time.time() - start_time
                work_time_remaining -= elapsed
                start_time = time.time()
                # Main countdown
                if not self.running or self.stop_event.is_set(): # Constant check for stop
                    break
                if self.root.winfo_exists():  # Check if the root window exists before updating
                    self.root.after(0, self.update_main_countdown, work_time_remaining)

            if not self.running or self.stop_event.is_set():
                break
            
            self.notify_user()

            # Break Interval
            break_time_remaining = self.break_duration
            start_time = time.time()
            while self.running and break_time_remaining > 0:
                time.sleep(min(0.05, break_time_remaining))  # Update every 0.05 seconds
                elapsed = time.time() - start_time
                break_time_remaining -= elapsed
                start_time = time.time()
                if not self.running or self.stop_event.is_set() or self.notif_stopped_event.is_set(): # COULD CAUSE ISSUES WITH RESTARTING MAIN TIMER
                    '''----CRITICAL LINE FOR MAIN TIMER RESET UPON NOTIFICATION WINDOW ESCAPE----'''
                    self.notif_stopped_event.clear()
                    break
                if self.root.winfo_exists():
                    self.root.after(0, self.update_main_countdown, break_time_remaining)

    def update_main_countdown(self, time_remaining):
        if not self.running or self.stop_event.is_set():
            return
        hours = int(time_remaining // 3600)
        minutes = int((time_remaining % 3600) // 60)
        seconds = int(time_remaining % 60)
        countdown_text = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.root.after(0, self.main_countdown.config, {'text': countdown_text, 'fg': 'black'})

    def notify_user(self):
        # Ensure only one notification window is open
        if hasattr(self, 'top') and self.top.winfo_exists():
            return
            
        self.top = tk.Toplevel(self.root)
        self.top.attributes("-fullscreen", True)  # fullscreen
        self.top.attributes("-topmost", True)     # Ensure the window stays on top
        self.top.configure(bg='white')

        frame = tk.Frame(self.top, bg='white')
        frame.grid(row=0, column=0, sticky='nsew') # Center frame and expand to fill

        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_columnconfigure(0, weight=1)

        # Text holder for break_interval_countdown function updates
        self.countdown_label = tk.Label(self.top, text="", fg='black', bg='white', font=("Verdana", 48)) 
        self.countdown_label.grid(row=0, column=0, pady=20)

        self.icon_button = tk.Button(frame, image=self.icon_image, borderwidth=0, command=self.escape_notification_window)
        self.icon_button.grid(row=1, column=0, pady=20, padx=20)  # Centered at the bottom of the frame

        frame.update_idletasks()
        width = frame.winfo_reqwidth()
        height = frame.winfo_reqheight()
        self.top.geometry(f"{width}x{height}+{self.top.winfo_screenwidth()//2-width//2}+{self.top.winfo_screenheight()//2-height//2}")

        # start countdown
        self.break_interval_countdown(self.break_duration)

    def break_interval_countdown(self, count):
        if count >= 0 and self.running:
            self.countdown_label.config(text=f"Look 20 feet away for {count} seconds!")
            self.top.after(1000, self.break_interval_countdown, count - 1)  # update countdown every 1000 ms
        else:
            self.top.destroy()  # close notif window when countdown finishes


if __name__ == "__main__":
    root = tk.Tk()
    app = EyeRestApp(root)
    root.mainloop()
    

