# main.py
import multiprocessing
import os
import sys
from tkinter import PhotoImage
from model import OrganPlayerModel
from view import OrganPlayerView
from controller2 import OrganPlayerController

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

def main():
    # Create instances of the model, view, and controller
    model = OrganPlayerModel()
    view = OrganPlayerView()
    controller = OrganPlayerController(model, view)

    # Connect the view to the controller
    view.set_controller(controller)

    # Start the Tkinter main loop
    icon_path = os.path.join(BASE_DIR, 'images', 'organ.png')
    icon = PhotoImage(file=icon_path)
    view.iconphoto(True, icon)
    view.start_mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
