from tkinter import IntVar, ttk, font
import tkinter as tk
import copy
from Stops2 import *
from model import LibraryHymn, PlaylistHymn

PLAYLIST_TEXT_BG = "#343A40"
PLAYLIST_TEXT = "#f8f9fa"
LIBRARY_PARENT = "#ff7851"
LIBRARY_SELECTED = "#e99002"

#pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

class ScrolledTreeView(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        self.frame = tk.Frame(parent)  # Create a new frame to hold the Treeview and Scrollbar
        style = ttk.Style()
        style.configure('Treeview', rowheight=50)  # Increase row height
        style.configure("Vertical.TScrollbar", arrowsize=30)

        style.map('Treeview',
          background=[('selected', LIBRARY_SELECTED)],
          foreground=[('selected', 'white')])
        ttk.Treeview.__init__(self, self.frame, *args, **kwargs)  # Initialize the Treeview with the new frame as its parent
        self.vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.yview)  # Create a scrollbar for the Treeview
        self.configure(yscrollcommand=self.vsb.set)
        self.tag_configure("oddrow", background="lightgray")
        self.tag_configure("evenrow", background="white")
        self.tag_configure("parent", background=PLAYLIST_TEXT_BG, foreground=PLAYLIST_TEXT, font=("Helvetica", 10, "bold"),)
        self.tag_configure("text", background=PLAYLIST_TEXT_BG, foreground=PLAYLIST_TEXT, font=("Helvetica", 10, "bold"))
        self.tag_configure("notFound", background="red", foreground="white", font=("Helvetica", 10, "bold"))
        self.vsb.pack(side="right", fill="y")  # Pack the Scrollbar into the frame
        self.pack(side="left", fill="both", expand=True)  # Pack the Treeview into the frame

        self.frame.pack(fill='both', expand=True)  # Pack the frame into the parent widget

    def destroy(self):
        self.vsb.destroy()
        ttk.Treeview.destroy(self)
        self.frame.destroy()  # Destroy the frame when the ScrolledTreeView is destroyed

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        task_id = self.id
        self.id = None
        if task_id:
            self.widget.after_cancel(task_id)

    def showtip(self, event=None):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.hidetip()
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1,
                        font=("Arial", "10", "italic"), wraplength=200)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class Choice:
    def __init__(self, location, marker, selected_sections):
        self.text = marker.title
        self.state = IntVar(value=marker.is_selected)
        copy = marker
        self.data = copy
        self.selected_sections = selected_sections
        self.checkbutton = tk.Checkbutton(location, text=self.text, command=self.check,
                                        variable=self.state, onvalue=1, offvalue=0, anchor='w')
        self.checkbutton.pack()
        self.check()

    def check(self):
        state = self.state.get()
        if state == 1:
            self.data.is_selected = True
            if (self.data not in self.selected_sections):
                self.selected_sections.append(self.data)
        if state == 0:
            self.data.is_selected = False
            if (self.data in self.selected_sections):
                self.selected_sections.remove(self.data)

class SongSelectionWindow:
    def __init__(self, master, controller, hymn, context):
        self.hymn = None
        self.master = master
        self.controller = controller
        self.context = context
        # Create a new window
        self.new_window = tk.Toplevel(self.master)
        self.new_window.title(f"{hymn.hymn_number} {hymn.title}")
        self.new_window.attributes('-topmost', 'true')
        self.new_window.resizable(False, False)
        self.new_window.focus_force()
        container = tk.Frame(self.new_window)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        left_frame = tk.Frame(container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_frame = tk.Frame(container)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.new_window.protocol("WM_DELETE_WINDOW", lambda : self.onClose())

        # Create a dictionary to store the checkboxes
        self.selected_sections = []

        # Determine the markers based on context
        if context == "library_edit" or context == "add_to_playlist":
            markers = copy.deepcopy(hymn.markers)
        elif context == "playlist":
            for marker in copy.deepcopy(hymn.markers):
                if marker not in hymn.selected_markers:
                    marker.is_selected = False
            selected_titles = [marker.title for marker in hymn.selected_markers]
            markers = hymn.selected_markers + [marker for marker in hymn.markers if marker.title not in selected_titles]
            markers = self.controller.sort_markers(markers)

        # For each marker, create a checkbox and add it to the new window
        for marker in markers:
            Choice(left_frame, marker, self.selected_sections)

        # Create a dictionary to store the OptionMenus
        track_channels = {}

        # Get the channel names and values
        channel_names = [channel.name for channel in Channels]

        # For each track, create a label and an OptionMenu and add them to the new window
        for i, (input_channel, output_channel) in enumerate(hymn.track_names.items()):
            # Create a label for the track
            label_text = Channels.get_channel_name(output_channel)
            track_label = tk.Label(right_frame, text=label_text)
            track_label.grid(row=i, column=2, sticky="w")

            # Create an OptionMenu for the track                  
            channel_var = tk.StringVar(value=label_text)
            channel_menu = tk.OptionMenu(right_frame, channel_var, *channel_names)
            channel_menu.grid(row=i, column=3, sticky="w")

            # Store the OptionMenu in the dictionary
            track_channels[int(input_channel)] = channel_var
        button_frame = tk.Frame(container)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        # add a checkbox for prerecorded registration
        self.use_registration = tk.BooleanVar(value=True if hymn.has_sysex else False)
        if (hymn.has_sysex):
            registration_checkbutton = tk.Checkbutton(button_frame, text="Use Prerecorded Registration", variable=self.use_registration)
            registration_checkbutton.pack()

        # Add a checkbox to use default organ stops for marker sections
        self.use_default_stops = tk.BooleanVar(value=True)
        default_checkbutton = tk.Checkbutton(button_frame, text="Use Default Stops", variable=self.use_default_stops)
        default_checkbutton.pack()
        # Add a label for the bpm
        bpm_label = tk.Label(right_frame, text="bpm")
        bpm_label.grid(row=len(hymn.track_names), column=2, sticky="w")

        # Add an entry for the bpm
        self.use_default_bpm = tk.BooleanVar(value=False)
        self.is_prelude = tk.BooleanVar(value=False)
        self.bpm_var = tk.StringVar(value = int(hymn.new_bpm))
        bpm_entry = tk.Entry(right_frame, textvariable=self.bpm_var)
        bpm_entry.grid(row=len(hymn.track_names), column=3, sticky="w")
        default_bpm_checkbutton = tk.Checkbutton(right_frame, text="Use Default BPM", variable=self.use_default_bpm, command=lambda: self.toggle_bpm_entry(hymn))
        default_bpm_checkbutton.grid(row=len(hymn.track_names)+1, column=3, sticky="w")
        is_prelude_checkbutton = tk.Checkbutton(right_frame, text="Is Prelude", variable=self.is_prelude)
        is_prelude_checkbutton.grid(row=len(hymn.track_names)+2, column=3, sticky="w")

        if (hymn.new_bpm == hymn.bpm):
            default_bpm_checkbutton['state'] = tk.DISABLED

        self.bpm_var.trace("w", lambda *args: self.on_bpm_var_change(hymn, self.bpm_var, default_bpm_checkbutton))

        # Add a submit button to the new window
        submit_button = tk.Button(button_frame, text="Submit", command=lambda: self.submit(track_channels, hymn))
        cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: self.new_window.destroy())
        submit_button.pack()
        cancel_button.pack()
        self.new_window.bind('<Escape>', lambda event: self.new_window.destroy())
        self.new_window.wait_window(self.new_window)

        # Define the function to be called when the value of the StringVar changes
    def on_bpm_var_change(self, hymn, bpm_var, default_bpm_checkbutton):
        if bpm_var.get() != hymn.bpm:
            default_bpm_checkbutton['state'] = tk.NORMAL

    def toggle_bpm_entry(self, hymn):
        assert isinstance(self.use_default_bpm, tk.BooleanVar), "self.use_default_bpm is not initialized"
        assert isinstance(self.bpm_var, tk.StringVar), "self.bpm_var is not initialized"
        assert hymn is not None, "hymn is None"
        assert hymn.bpm is not None, "hymn.bpm is None"
        assert hymn.new_bpm is not None, "hymn.new_bpm is None"

        if self.use_default_bpm.get():
            self.bpm_var.set(int(hymn.bpm))
        else:
            self.bpm_var.set(int(hymn.new_bpm))


    def submit(self, track_channels, hymn):
        assert isinstance(track_channels, dict), "track_channels must be a dictionary"
        assert hymn is not None, "hymn must not be None"

        self.controller.selected_stops = None
        default_stops = self.controller.get_default_stops()

        if self.context == "library_edit":
            for marker in hymn.markers:
                marker.is_selected = False
            marker_dict = {marker.title: marker for marker in self.selected_sections}
            marker_dict.update({marker.title: marker for marker in hymn.markers if marker.title not in marker_dict})

            markers = list(marker_dict.values())
            markers = self.controller.sort_markers(markers)


        if self.use_default_stops.get():
            for section in self.selected_sections:
                if self.is_prelude == True:
                        section.stops = self.controller.get_preset_stops("prelude")
                if not self.use_registration.get():
                        section.stops = default_stops
        else:
            for section in self.selected_sections:
                # Show a new window to select the stops for this section
                StopSelectionWindow(self.master, section, self.controller, hymn.markers, context="library")
                if self.controller.selected_stops is not None:
                    section.stops = self.controller.selected_stops
                else:
                    section.stops = default_stops
        if self.context == "library_edit":
            hymn.markers = markers
        else:
            hymn.selected_markers = self.selected_sections
        hymn.new_bpm = self.bpm_var.get()
        for channel in hymn.track_names.keys():
            channel_name = track_channels[int(channel)].get()
            channel_enum = Channels[channel_name]
            hymn.track_names[channel] = int(channel_enum.value)
        hymn.use_default_stops = self.use_default_stops.get()
        hymn.use_registration = self.use_registration.get()
        self.hymn = hymn
        self.new_window.destroy()

    def onClose(self):
        self.new_window.destroy()
        return self.hymn

class StopSelectionWindow:
    def __init__(self, master, section, controller, hymn_markers, context):
        self.master = master
        self.context = context
        self.controller = controller
        if (context == "library"):
            if self.controller.selected_stops is None:
                self.selected_stops = next((marker.stops for marker in hymn_markers if marker.title == section.title), None)
            else:
                self.selected_stops = self.controller.selected_stops
            if self.selected_stops is None:
                self.selected_stops = self.controller.get_default_stops()
            title = section.title
        else:
            self.selected_stops = []
            title = "current section"
        self.stop_selection_window = tk.Toplevel(self.master)
        self.stop_selection_window.title(f"Select stops for {title}")
        self.stop_selection_window.maxsize(1500, 900)

        self.stop_buttons = []
        self.my_font = font.Font(family='Helvetica', size=12, weight='bold')

        self.stop_type_colors = {
            StopType.REED: "#8B0000",
        }
        tablet_frame = tk.Frame(self.stop_selection_window)
        canvas = tk.Canvas(tablet_frame)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        for row, (manual_name, manual) in enumerate(manuals.items()):
            self.create_manual_frame(canvas, row, manual_name, manual)
        tablet_frame.grid(row=0, column=1)

        if self.context == "library":
            submit_button = tk.Button(self.stop_selection_window, text="Submit", command=self.submit_stops)
            cancel_button = tk.Button(self.stop_selection_window, text="Cancel", command=self.cancel_stops)
            submit_button.grid(row=4, columnspan=len(self.stop_buttons))
#
        preset_frame = tk.LabelFrame(self.stop_selection_window, text="Preset Buttons", padx=10 )
        preset_frame.grid(row=0, column=0, sticky="nesw")

        clear_preset = ttk.Button(preset_frame, bootstyle="danger-outline", text="Clear Stops", command=lambda: self.enable_stops("clear"))
        prelude_preset = ttk.Button(preset_frame, bootstyle="outline", text="Prelude", command=lambda: self.enable_stops("prelude"))
        intro_preset = ttk.Button(preset_frame, bootstyle="outline",  text="Intro", command=lambda: self.enable_stops("intro"))
        g1_preset = ttk.Button(preset_frame, bootstyle="outline",  text="G1", command=lambda: self.enable_stops("g1"))
        g2_preset = ttk.Button(preset_frame, bootstyle="outline",  text="G2", command=lambda: self.enable_stops("g2"))
        g3_preset = ttk.Button(preset_frame, bootstyle="outline",  text="G3", command=lambda: self.enable_stops("g3"))
        g4_preset = ttk.Button(preset_frame, bootstyle="outline",  text="G4", command=lambda: self.enable_stops("g4"))
        g5_preset = ttk.Button(preset_frame, bootstyle="outline",  text="G5", command=lambda: self.enable_stops("g5"))
        full_organ_preset = ttk.Button(preset_frame, bootstyle="outline",  text="Full Organ", command=lambda: self.enable_stops("full"))

        presets = [clear_preset, prelude_preset, intro_preset, g1_preset, g2_preset, g3_preset, g4_preset, g5_preset, full_organ_preset]

        for i, preset in enumerate(presets):
            preset.grid(row=i, column=0, sticky='ew')  # Place each button in its own row
            preset_frame.grid_rowconfigure(i, weight=1)  # Set the weight of each row to 1
        
        self.stop_selection_window.wait_window()

    def create_manual_frame(self, tablet_frame, row, manual_name, manual):
        frame = tk.LabelFrame(tablet_frame, text=manual_name, padx=10, pady=10, borderwidth=2, relief=tk.GROOVE)
        for column, (_, stop) in enumerate(manual.stops.items()):
            self.create_stop_button(frame, row, column, stop)
        frame.grid(row=row, column=1, sticky="w")

    def create_stop_button(self, frame, row, column, stop):
        color = self.stop_type_colors.get(stop.stop_type, "black")
        button = tk.Button(frame, text=stop.label_text, bg="gray", fg=color, width=8, height=4, font=self.my_font, autostyle=False)
        button.config(command=lambda btn=button, stp=stop: self.update_stop(stp, btn))
        button.grid(row=row, column=column, sticky="w")
        if stop in self.selected_stops:
            button['bg'] = "#fffff2"
            button['activebackground'] = "#fffff2"
            stop.is_engaged = True
        self.stop_buttons.append(button)

    def enable_stops(self, preset):
        if preset == "prelude":
            self.selected_stops = self.controller.get_preset_stops("prelude")
        elif preset == "clear":
            self.selected_stops = []
        elif preset == "intro":
            self.selected_stops = self.controller.get_preset_stops("intro")
        elif preset == "g1":
            self.selected_stops = self.controller.get_preset_stops("g1")
        elif preset == "g2":
            self.selected_stops = self.controller.get_preset_stops("g2")
        elif preset == "g3":
            self.selected_stops = self.controller.get_preset_stops("g3")
        elif preset == "g4":
            self.selected_stops = self.controller.get_preset_stops("g4")
        elif preset == "g5":
            self.selected_stops = self.controller.get_preset_stops("g5")
        elif preset == "full":
            self.selected_stops = self.controller.get_preset_stops("full")
        for button in self.stop_buttons:
            button['bg'] = "gray"
            stop = next((stop for stop in self.selected_stops if stop.label_text == button['text']), None)
            if stop is not None:
                button['bg'] = "white"
                button['bg'] = "#fffff2"
                button['activebackground'] = "#fffff2"
                stop.is_engaged = True
        if self.context == "playlist":
            self.send_button_states_to_controller()

    def update_stop(self, stop, button):
        if button['bg'] == "gray":
            button['bg'] = "#fffff2"
            button['activebackground'] = "#fffff2"
            stop.is_engaged = True
            self.selected_stops.append(stop)
        else:
            button['bg'] = "gray"
            stop.is_engaged = False
            self.selected_stops.remove(stop)
        if self.context == "playlist":
            self.send_button_states_to_controller()

    def send_button_states_to_controller(self):
        self.controller.receive_engaged_stops(self.selected_stops)

    def submit_stops(self):
        self.controller.selected_stops = self.selected_stops
        self.stop_selection_window.destroy()

    def cancel_stops(self):
        self.controller.selected_stops = self.controller.get_default_stops()
        self.stop_selection_window.destroy()
