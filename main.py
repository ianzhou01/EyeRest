import tkinter as tk
from tkinter import messagebox
import threading
import time

class TwentyTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TwentyTime")

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
        self.work_entry = tk.Entry(self.work_frame, textvariable=self.work_value)
        self.work_entry.pack(side=tk.LEFT)
        
        # create dropdown for work units
        self.work_unit = tk.StringVar(value="minutes")  # Default unit
        self.work_unit_button = tk.Button(self.work_frame, text=self.work_unit.get(), command=self.toggle_work_unit_menu)
        self.work_unit_button.pack(side=tk.LEFT)
        
        self.work_unit_menu = tk.Menu(root, tearoff=0)
        self.work_unit_menu.add_command(label="minutes", command=lambda: self.set_work_unit("minutes"))
        self.work_unit_menu.add_command(label="seconds", command=lambda: self.set_work_unit("seconds"))

        # make frame for break interval
        self.break_frame = tk.Frame(root)
        self.break_frame.pack(pady=10)

        # make label and entry for break interval
        self.break_label = tk.Label(self.break_frame, text="Break Duration:")
        self.break_label.pack(side=tk.LEFT)
        
        self.break_value = tk.StringVar(value="20")  # Default value
        self.break_entry = tk.Entry(self.break_frame, textvariable=self.break_value)
        self.break_entry.pack(side=tk.LEFT)
        
        # dropdown for break units
        self.break_unit = tk.StringVar(value="seconds")  # Default unit
        self.break_unit_button = tk.Button(self.break_frame, text=self.break_unit.get(), command=self.toggle_break_unit_menu)
        self.break_unit_button.pack(side=tk.LEFT)
        
        self.break_unit_menu = tk.Menu(root, tearoff=0)
        self.break_unit_menu.add_command(label="minutes", command=lambda: self.set_break_unit("minutes"))
        self.break_unit_menu.add_command(label="seconds", command=lambda: self.set_break_unit("seconds"))

        # start/stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.running = False
        self.timer_thread = None
        self.stop_event = threading.Event()

        # Bind close event to cleanup func
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_work_unit_menu(self):
        self.work_unit_menu.post(self.work_unit_button.winfo_rootx(), self.work_unit_button.winfo_rooty() + self.work_unit_button.winfo_height())

    def set_work_unit(self, unit):
        self.work_unit.set(unit)
        self.work_unit_button.config(text=unit)

    def toggle_break_unit_menu(self):
        self.break_unit_menu.post(self.break_unit_button.winfo_rootx(), self.break_unit_button.winfo_rooty() + self.break_unit_button.winfo_height())

    def set_break_unit(self, unit):
        self.break_unit.set(unit)
        self.break_unit_button.config(text=unit)

    def start_timer(self):
        if self.running:
            return
        
        try:
            # Get values and units
            work_value = int(self.work_value.get())
            work_unit = self.work_unit.get()
            break_value = int(self.break_value.get())
            break_unit = self.break_unit.get()
            
            # Convert work interval and break duration to seconds
            if work_unit == "minutes":
                self.work_interval = work_value * 60
            else:
                self.work_interval = work_value
            
            if break_unit == "minutes":
                self.break_duration = break_value * 60
            else:
                self.break_duration = break_value
            # Error checking
            if self.work_interval <= 0 or self.break_duration <= 0:
                raise ValueError("Intervals must be positive numbers.")
            
            self.running = True
            self.stop_event.clear()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            if self.timer_thread is None or not self.timer_thread.is_alive():
                self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
                self.timer_thread.start()
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers for the intervals.")

    def stop_timer(self):
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if hasattr(self, 'top') and self.top.winfo_exists():
            self.top.destroy()

    def run_timer(self):
        while self.running:
            if self.stop_event.is_set():
                break
            
            try:
                time.sleep(self.work_interval)  # work interval (sec)
                if not self.running or self.stop_event.is_set():
                    break
                self.notify_user()
                time.sleep(self.break_duration)  # break duration (sec)
            except Exception as e:
                print(f"Exception in timer thread: {e}")
                break

    def notify_user(self):
        # Ensure only one notification window is open
        if hasattr(self, 'top') and self.top.winfo_exists():
            return
        
        self.top = tk.Toplevel(self.root)
        self.top.attributes("-fullscreen", True)  # fullscreen
        self.top.configure(bg='black')
        self.countdown_label = tk.Label(self.top, text="", fg='white', bg='black', font=("Arial", 48))
        self.countdown_label.pack(expand=True)
        
        # Start the countdown
        self.countdown(self.break_duration)

    def countdown(self, count):
        if count >= 0 and self.running:
            self.countdown_label.config(text=f"Look 20 feet away for {count} seconds!")
            self.top.after(1000, self.countdown, count - 1)  # update countdown every 1000 ms
        else:
            self.top.destroy()  # close notif window when countdown finishes

    def on_closing(self):
        self.stop_timer()  # stop timer if running
        if self.timer_thread is not None:
            self.stop_event.set()  # signal thread to stop
            self.timer_thread.join(timeout=1)  # add timeout to wait for timer to finish
        self.root.destroy()  # close the main window and exit

if __name__ == "__main__":
    root = tk.Tk()
    app = TwentyTimeApp(root)
    root.mainloop()
