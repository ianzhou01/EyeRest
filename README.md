# EyeRest
### Functionality
- This is a simple app built on Tkinter (included in Python) to facilitate regular eye rest while working on the computer.
- The current version of the app freezes the screen during breaks with overlay.
- The stop button resets the timer; the timer will begin from 0 until the new (if updated) work interval has elapsed.
### Implementation
- This script can be run locally or made into an executable on Windows via pyinstaller.
- First, ensure you have the latest version of Python (this was written with Python 3.12.3; it may run on earlier versions, but that is not guaranteed).
- Second, ensure you have pyinstaller installed (simply run "pip install pyinstaller" if not).
- Third, using the terminal, navigate to the directory where you have main.py, and run "pyinstaller --onefile --windowed main.py"; this will generate a folder in that directory called dist, in which the executable will be located. 
