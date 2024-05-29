# PDF Merger
An application to merge multipe pdf files in a single one. This get handy when you need to print multiple pdf files that has a lot of pages and don't have some paid applications.

# Requirements
This application, to run, requires: PyPDF2, PyQt6, PyQt6_sip. Use the command python -m pip install -r requirements.txt to get the needed libraries.

# Execution
You can execute the application with pyhton3 main.py.

# Compile For Windows
You can compile this program with pyinstaller.

Install pyinstaller with pip: 
pip install pyinstaller
or
python3 -m pip install pyinstaller

Run this command to compile main.py:
pyinstaller --onefile --windowed main.py
(this will create an .exe file under the "dist" folder)

