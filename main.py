#!/usr/bin/env python3

# This script requires a virtual environment with the packages from requirements.txt
# To create and activate the venv:
# python -m venv venv
# source venv/bin/activate (macOS/Linux) or venv\Scripts\activate (Windows)
# pip install -r requirements.txt

import tkinter as tk
from ui.app import QuestionsSim

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionsSim(root)
    root.mainloop()