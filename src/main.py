# main.py
import multiprocessing
from model import OrganPlayerModel
from view import OrganPlayerView
from controller2 import OrganPlayerController

def main():
    # Create instances of the model, view, and controller
    model = OrganPlayerModel()
    view = OrganPlayerView()
    controller = OrganPlayerController(model, view)

    # Connect the view to the controller
    view.set_controller(controller)

    # Start the Tkinter main loop
    view.start_mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
