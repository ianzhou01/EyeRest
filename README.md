# EyeRest
### Functionality
- This is a simple app built on Tkinter (included in Python) to facilitate regular eye rest while working on computers.
- The current version of the app covers the screen during breaks with overlay; the escape icon exits this notification countdown and starts a new cycle.
- The stop button resets the timer; the timer will begin from 0 until the new (if updated) work interval has elapsed.
### Installation
- This app is currently configured only for Windows. Simply download EyeRest.exe and run the program (you may need to override computer warnings).
- Generally, manual installation is not recommended. Some windows machines may require .ico or .exe files instead of .png files, and main.py will need to be refactored to reflect the file conversion. Pillow can be installed for automatic conversion from .png to .ico/.exe.
- First, ensure you have Python installed (this was written with Python 3.12.3; it may run on earlier versions, but that is not guaranteed).
- Second, install PyInstaller if you haven't already (simply run "pip install pyinstaller" if not).
- Third, download main.py, EyeRest.spec, clock.png, and escape.png, all into one directory/folder of your choice. Creating a new folder is recommended. (If desired, the future file icon "clock.png" can be changed to an icon of your choosing; simply download the new icon in the same folder and edit "EyeRest.spec" in a text editor and alter the data dependency for "clock.png" to the name of the new icon.)
- Fourth, using the terminal, navigate to the directory/folder where you have main.py, and run "pyinstaller EyeRest.spec"; this will generate another directory in that directory called "dist."
- The executable is located within the dist folder.
