# view.py
import os
import tkinter as tk
from tkinter import Checkbutton, IntVar, ttk
from tkinter import font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from natsort import natsorted
from Stops2 import *

PLAYLIST_TEXT_BG = "#343A40"
PLAYLIST_TEXT = "#f8f9fa"
LIBRARY_PARENT = "#ff7851"
LIBRARY_SELECTED = "#e99002"
basedir = os.path.dirname(os.path.abspath(__file__))

class ScrolledTreeView(ttk.Treeview):
    def __init__(self, parent, *args, **kwargs):
        self.frame = tk.Frame(parent)  # Create a new frame to hold the Treeview and Scrollbar
        style = ttk.Style()
        style.map('Treeview',
          background=[('selected', LIBRARY_SELECTED)],
          foreground=[('selected', 'white')])
        ttk.Treeview.__init__(self, self.frame, *args, **kwargs)  # Initialize the Treeview with the new frame as its parent

        self.vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.yview)  # Create the Scrollbar with the new frame as its parent
        self.configure(yscrollcommand=self.vsb.set)
        self.tag_configure("oddrow", background="white")
        self.tag_configure("evenrow", background="lightgray")
        self.tag_configure("parent", background=PLAYLIST_TEXT_BG, foreground=PLAYLIST_TEXT, font=("Helvetica", 10, "bold"),)
        self.tag_configure("text", background=PLAYLIST_TEXT_BG, foreground=PLAYLIST_TEXT, font=("Helvetica", 10, "bold"))
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
        self.state = IntVar(value=1)
        self.data = marker
        self.selected_sections = selected_sections
        self.checkbutton = Checkbutton(location, text=self.text, command=self.check,
                                        variable=self.state, onvalue=1, offvalue=0, anchor='w')
        self.checkbutton.pack()
        self.check()

    def check(self):
        state = self.state.get()
        if state == 1:
            self.selected_sections.append(self.data)
        if state == 0:
            self.selected_sections.remove(self.data)

class LibraryWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.stop_checkbuttons = []
        self.section_labels = []
        self.submit_button = None
        self.cancel_button = None

        self.title("Library")
        self.geometry("500x500")

        container = ttk.Frame(self)
        container.pack(side="top", fill="both",padx=10, pady=10, expand=True)

        self.library_frame = tk.Frame(container, padx=10, pady=10)
        self.library_frame.pack_forget()

        self.library_treeview = ScrolledTreeView(self.library_frame, columns=("Number", "Title", "ParentTitle", "Kind", "Key", "TimeSignature"), show="tree headings")
        self.library_treeview.heading("Number", text="#", command=lambda: self.treeview_sort_column("Number", False))
        self.library_treeview.heading("Title", text="Title", command=lambda: self.treeview_sort_column("Title", False))
        self.library_treeview.heading("Kind", text="Kind", command=lambda: self.treeview_sort_column("Kind", False))
        self.library_treeview.heading("Key", text="Key", command=lambda: self.treeview_sort_column("Key", False))  # New column
        self.library_treeview.heading("TimeSignature", text="Time Signature", command=lambda: self.treeview_sort_column("TimeSignature", False))  # New column
        self.library_treeview.column("Number", width=40, stretch="no")
        self.library_treeview.column("Title", stretch="yes", anchor="w")
        self.library_treeview.column("ParentTitle", width = 0, anchor="w")  # Text centered in column "ParentTitle"
        self.library_treeview.column("Kind", width = 50, stretch="no")
        self.library_treeview.column("Key", width = 40, stretch="no")  # New column
        self.library_treeview.column("TimeSignature", width=40, stretch="no")  # New column
        self.library_treeview.column("#0", width=0, stretch="no")
        self.library_treeview["displaycolumns"] = ("Number", "Title", "ParentTitle", "Kind", "Key")  # Include new columns
        self.add_button = ttk.Button(self, text="Add to Playlist", command=self.add_to_playlist)
        self.edit_button = ttk.Button(self, text="Edit Song",  state=tk.DISABLED)
        self.progress = ttk.Progressbar(container, orient="horizontal", length=200, mode="determinate")
        self.progress.place(relx=0.5, rely=0.45, anchor='center')
        self.library_treeview.bind("<Double-1>", lambda e: self.add_to_playlist())
        self.loading_label = tk.Label(container, text="Refreshing library...")
        self.loading_label.place(relx=0.5, rely=0.5, anchor='center')


        self.controller.load_library_files(reloadCache=False, total_files_callback=self.set_total_files, update_progress_callback=self.update_progress)
        self.withdraw()  # Hide the window until the library is loaded
        self.protocol('WM_DELETE_WINDOW', self.hide) 

    def set_total_files(self, total):
        self.progress['maximum'] = total

    def update_progress(self, value):
        self.progress['value'] = value
        self.update_idletasks()

    def show_library_frame(self):
        self.library_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.add_button.pack(side=tk.RIGHT, padx=(0, 40), pady=(0, 20))
        self.edit_button.pack(side=tk.RIGHT, padx=(0, 40), pady=(0, 20))
        self.loading_label.destroy()
        self.progress.destroy()

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()  # Show the window

    def treeview_sort_column(self, column, reverse):
        for parent in self.library_treeview.get_children(''):
            data = [(self.library_treeview.set(k, column), k) for k in self.library_treeview.get_children(parent)]
            data = natsorted(data, key=lambda x: x[0], reverse=reverse)

            for index, (_, k) in enumerate(data):
                self.library_treeview.move(k, parent, index)
                # Update the tags for the rows after sorting
                tag = "oddrow" if index % 2 else "evenrow"
                self.library_treeview.item(k, tags=(tag,))

        self.library_treeview.heading(column, command=lambda: self.treeview_sort_column(column, not reverse))


    def start_loading(self):
        self.library_treeview.pack_forget()
        self.loading_label.pack()

    def update_library_view(self, hymns):
        parent_items = {}
        for i, hymn in enumerate(hymns.values()):
            tag = "oddrow" if i % 2 else "evenrow"
            if hymn.kind == "DivineService":
                if hymn.hymn_number not in parent_items:
                    parent_items[hymn.hymn_number] = self.library_treeview.insert("", "end", values=("",  f"{hymn.hymn_number}", "", "", "", ""), tags=("parent",))
                    self.library_treeview.item(parent_items[hymn.hymn_number], open=True)
                    self.library_treeview.insert(parent_items[hymn.hymn_number], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"  ), tags=(tag,))
                else:
                    self.library_treeview.insert(parent_items[hymn.hymn_number], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
            else:
                if hymn.kind not in parent_items:
                    parent_items[hymn.kind] = self.library_treeview.insert("", "end", values=("", f"{hymn.kind}", "", "", "", ""), tags=("parent",))
                    self.library_treeview.item(parent_items[hymn.kind], open=True)
                    self.library_treeview.insert(parent_items[hymn.kind], "end", values=(hymn.hymn_number, hymn.title, "",  hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
                else:
                    self.library_treeview.insert(parent_items[hymn.kind], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
    def add_to_playlist(self):
        selected_item = self.library_treeview.selection()
        if selected_item:
            values = self.library_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_library(values)
            if hymn is None:
                return    
            # Create a new window
            new_window = tk.Toplevel(self)
            new_window.title("Select Options")
            container = tk.Frame(new_window)
            container.pack(side="top", fill="both", expand=True)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            container.grid_columnconfigure(1, weight=1)
            left_frame = tk.Frame(container)
            left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            right_frame = tk.Frame(container)
            right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

            # Create a dictionary to store the checkboxes
            self.selected_sections = []

            # For each marker, create a checkbox and add it to the new window
            for marker in hymn.markers:
                Choice(left_frame, marker, self.selected_sections)

            # Create a dictionary to store the OptionMenus
            track_channels = {}

            # Get the channel names and values
            channel_names = [channel.name for channel in Channels]

            # For each track, create a label and an OptionMenu and add them to the new window
            for i, (channel, instrument)  in enumerate(hymn.track_names.items()):
                channel = int(channel)
                # Create a label for the track
                track_label = tk.Label(right_frame, text=instrument)
                track_label.grid(row=i, column=2, sticky="w")

                # Create an OptionMenu for the track                  
                channel_var = tk.StringVar(value=channel_names[i % len(channel_names)])
                channel_menu = tk.OptionMenu(right_frame, channel_var, *channel_names)
                channel_menu.grid(row=i, column=3, sticky="w")

                # Store the OptionMenu in the dictionary
                track_channels[channel] = channel_var
            button_frame = tk.Frame(container)
            button_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
            # Add a checkbox to use default organ stops for marker sections
            self.use_default_stops = tk.BooleanVar(value=True)

            default_checkbutton = tk.Checkbutton(button_frame, text="Use Default Stops", variable=self.use_default_stops)
            default_checkbutton.pack()
            # Add a label for the bpm
            bpm_label = tk.Label(right_frame, text="bpm")
            bpm_label.grid(row=len(hymn.track_names), column=2, sticky="w")

            # Add an entry for the bpm
            self.use_default_bpm = tk.BooleanVar(value=False)
            self.bpm_var = tk.StringVar(value = int(hymn.new_bpm))
            bpm_entry = tk.Entry(right_frame, textvariable=self.bpm_var)
            bpm_entry.grid(row=len(hymn.track_names), column=3, sticky="w")
            default_bpm_checkbutton = tk.Checkbutton(right_frame, text="Use Default BPM", variable=self.use_default_bpm, command=lambda: self.toggle_bpm_entry(hymn))

            default_bpm_checkbutton.grid(row=len(hymn.track_names)+1, column=3, sticky="w")

            if (hymn.new_bpm == hymn.bpm):
                default_bpm_checkbutton['state'] = tk.DISABLED

            self.bpm_var.trace("w", lambda *args: self.on_bpm_var_change(hymn, self.bpm_var, default_bpm_checkbutton))

            # Add a submit button to the new window
            submit_button = tk.Button(button_frame, text="Submit", command=lambda: self.submit(new_window, track_channels, hymn))
            cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: new_window.destroy())
            submit_button.pack()
            cancel_button.pack()
            new_window.bind('<Escape>', lambda event: new_window.destroy())

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

    def submit(self, new_window, track_channels, hymn):
        default_stops = self.controller.get_default_stops()

        if self.use_default_stops.get():
            for section in self.selected_sections:
                section.stops = default_stops
        else:
            for section in self.selected_sections:
                # Show a new window to select the stops for this section
                self.show_stop_selection_window(section)
                if self.selected_stops is not None:
                    section.stops = self.selected_stops
                else:
                    section.stops = default_stops
        hymn.selected_markers = self.selected_sections
        hymn.new_bpm = self.bpm_var.get()
        for channel in hymn.track_names.keys():
            channel_name = track_channels[int(channel)].get()
            channel_enum = Channels[channel_name]  # Convert the string back to the enum
            hymn.track_names[channel] = int(channel_enum.value)  # Get the integer part of the enum

        self.controller.add_to_playlist(hymn)
        new_window.destroy()

    def show_stop_selection_window(self, section):
        # Create a new window to select the stops for the section
        self.stop_selection_window = tk.Toplevel(self)
        self.stop_selection_window.title(f"Select stops for {section.title}")

        self.stop_buttons = []
        my_font = font.Font(family='Helvetica', size=12, weight='bold')
        self.selected_stops = []
        max_rows = 0
        for row, (_, manual) in enumerate(manuals.items()):
            max_rows = max_rows + 1
            buttons = []
            for column, (_, stop) in enumerate(manual.stops.items()):
                color = "#8B0000" if stop.stop_type == StopType.REED else "black"
                button = tk.Button(self.stop_selection_window, text=stop.label_text, bg="gray", fg=color, width=10, height=5, font=my_font)
                button.config(command=lambda btn=button, stp=stop: self.update_stop(stp, btn))
                button.grid(row=row, column=column, sticky="w")
                buttons.append(button)
            self.stop_buttons.append(buttons)

        self.submit_button = tk.Button(self.stop_selection_window, text="Submit", command=self.submit_stops)
        self.cancel_button = tk.Button(self.stop_selection_window, text="Cancel", command=self.cancel_stops)
        self.submit_button.grid(row=max_rows + 3, columnspan=len(self.stop_buttons))
        #self.update_stop_selection_columns()
        self.wait_window(self.stop_selection_window)

    def update_stop(self, stop, button):
        if button['bg'] == "gray":
            button['bg'] = "white"
            stop.is_engaged = True
            self.selected_stops.append(stop)
        else:
            button['bg'] = "gray"
            stop.is_engaged = False
            self.selected_stops.remove(stop)


    def submit_stops(self):
        # Do something with selected_stops
        self.stop_selection_window.destroy()

    def cancel_stops(self, new_window):
        self.selected_stops = self.controller.get_default_stops()
        new_window.destroy()


class OrganPlayerView(tk.Tk):
    """
    This class represents the view for the AutoBach Organ Player.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the OrganPlayerView.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.style = ttk.Style("yeti")
        default_font = tk.font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=12)
        self.option_add("*Font", default_font)
        self.minsize(120, 450)
        self.maxsize(1604, 1248)
        self.resizable(0,  0)
        icon_path = os.path.join(basedir, 'images', 'organ.ico')
        self.iconbitmap(icon_path)
        self.title("AutoBach Organ Player")
        self.configure(relief="ridge")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.left_frame = tk.Frame(container)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.playlistHeader = tk.Label(self.left_frame, text="PlayList", font=("Helvetica", 14, "bold"))
        self.playlistHeader.pack(side=tk.TOP)
        self.playlist_treeview = ScrolledTreeView(self.left_frame, columns=("Number", "Title", "Selected"),
                                        show="headings")

        self.playlist_treeview.column("Number", width=40, stretch="no")
        self.playlist_treeview.heading("Number", text="#")
        self.playlist_treeview.heading("Title", text="Title")
        self.playlist_treeview.heading("Selected", text="Selected")
        self.playlist_treeview["displaycolumns"] = ("Number", "Title", "Selected")
        self.playlist_treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)

        self.playlist_treeview.pack(side=tk.BOTTOM, fill="both", expand=True)

        # Create a new frame for the buttons
        self.button_frame = tk.Frame(container)
        self.button_frame.grid(row=0, column=1, sticky="nsew")

        # Create the buttons
        self.add_button = ttk.Button(self.button_frame, text="Add to Playlist",  command=self.show_library_window)
        self.add_text = ttk.Button(self.button_frame, text="Add Text", command=self.show_seperator_window)
        self.remove_button = ttk.Button(self.button_frame, text="Remove from Playlist", command=self.remove_from_playlist)
        self.edit_button = ttk.Button(self.button_frame, text="Edit Song", state=tk.DISABLED)
        self.move_up_button = ttk.Button(self.button_frame, text="Move Item Up", command=self.move_up)
        self.move_down_button = ttk.Button(self.button_frame, text="Move Item Down", command=self.move_down)


        # # Add the buttons to the frame
        for i in range(10):
            self.button_frame.grid_rowconfigure(i, weight=1)

        # Add the buttons to the frame
        self.add_button.grid(row=1, column=0, sticky="nsew", pady=(28, 3))
        CreateToolTip(self.add_button, "Add a song to the playlist")
        self.remove_button.grid(row=2, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.remove_button, "Remove a song from the playlist")
        self.add_text.grid(row=3, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.add_text, "Add a text seperator to the playlist")
        self.edit_button.grid(row=4, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.edit_button, "Edit a song in the playlist")
        self.move_up_button.grid(row=5, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.move_up_button, "Move a song up in the playlist")
        self.move_down_button.grid(row=6, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.move_down_button, "Move a song down in the playlist")

        self.right_frame = tk.Frame(container)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=20)
        #extra space
        self.right_frame.grid_rowconfigure(0, minsize=9, weight=0)
        #Song Info Box
        self.right_frame.grid_rowconfigure(1, weight=1)
        #Song Control Box
        self.right_frame.grid_rowconfigure(2, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
    #    self.right_frame.grid_columnconfigure(1, weight=1)


        self.current_Frame = tk.LabelFrame(self.right_frame, text="Song Info", padx=20, pady=20, borderwidth=2, relief=tk.GROOVE)
        self.current_Frame.grid(row=1, column=0, sticky="nwe")  # Use grid instead of pack

        self.current_song_title = tk.Label(self.current_Frame, text='''Current Song''')
        self.current_song = tk.Label(self.current_Frame)
        self.current_section_title = tk.Label(self.current_Frame, text='''Current Section''')
        self.current_section = tk.Label(self.current_Frame)

        self.current_song_title.grid(row=0, column=0, sticky="w")
        self.current_song.grid(row=0, column=1, sticky="e")
        self.current_section_title.grid(row=1, column=0, sticky="w")
        self.current_section.grid(row=1, column=1, sticky="e")

        self.control_Frame = tk.LabelFrame(self.right_frame, text="Song Control", padx=20, pady=5, borderwidth=2, relief=tk.GROOVE)
        self.button_grid = tk.Frame(self.control_Frame, pady=10)
        self.button_grid.grid_rowconfigure(0, weight=1)
        self.button_grid.grid_columnconfigure(0, weight=1)
        self.button_grid.grid_columnconfigure(1, weight=1)

        self.section_progress_bar = ttk.Progressbar(self.control_Frame, orient="horizontal", length=200, mode="determinate", maximum=100)
        self.stop_button = ttk.Button(self.button_grid, bootstyle=DANGER, state=tk.DISABLED, text='''Stop''')
        self.play_button = ttk.Button(self.button_grid, bootstyle=SUCCESS, state=tk.DISABLED,  text='''Play''')

        self.bpm_var = tk.StringVar()  # Holds the value of the bpm entry
        self.bpm_entry = ttk.Entry(self.control_Frame, textvariable=self.bpm_var)
        self.show_stop_selection_window_button = ttk.Button(self.control_Frame, text="Show Stop Selection Window", bootstyle=INFO, state=tk.DISABLED, command=self.show_stop_selection_window)    
        self.bpm_button = ttk.Button(self.control_Frame, text="Change bpm", bootstyle=INFO, state=tk.DISABLED, command=self.change_bpm)

        self.control_Frame.grid(row=2, column=0, sticky="nwe")  # Use grid instead of pack
        #progress bar
        self.control_Frame.grid_rowconfigure(0, weight=1)
        #button grid
        self.control_Frame.grid_rowconfigure(1, weight=1)
        #bpm entry
        self.control_Frame.grid_rowconfigure(2, weight=1)
        #stop selection button
        self.control_Frame.grid_rowconfigure(3, weight=1)
        self.control_Frame.grid_columnconfigure(0, weight=1)
        self.control_Frame.grid_columnconfigure(1, weight=1)

        #inside control frame
        self.section_progress_bar.grid(row=0, column=0, columnspan=2)
        self.button_grid.grid(row=1, column=0, columnspan=2, sticky="nwe", pady=2)  # Use grid instead of pack
        self.play_button.grid(row=0, column=0)  # Use grid instead of pack
        self.stop_button.grid(row=0, column=1)  # Use grid instead of pack
        self.bpm_entry.grid(row=2, column=0, sticky="w", pady=2)  # Adjust the row and column as needed
        self.bpm_button.grid(row=2, column=1, sticky="w", pady=2)  # Adjust the row and column as needed

        self.show_stop_selection_window_button.grid(row=3, column=0, columnspan=2, pady=2)  # Adjust the row and column as needed
        CreateToolTip(self.show_stop_selection_window_button, "Edit the stops while the song is playing")
   #     self.transpose_checkbox.grid(row=4, column=0, sticky="w")  # Adjust the row and column as needed

        # self.Button3 = tk.Button(self, text='''Select from Library''')
        self.menu_bar = tk.Menu(self)

        self.filemenu = tk.Menu(self.menu_bar, tearoff=0)
        self.midi_menu = tk.Menu(self.menu_bar, tearoff=0)

        self.menu_bar.add_cascade(label="File", menu=self.filemenu)
        self.menu_bar.add_cascade(label="Midi", menu=self.midi_menu)

        # Add the file menu to the main menu bar
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.selected_device = tk.StringVar(value="")

        # Set the main menu bar to be the menu for the application
        self.config(menu=self.menu_bar)

    def on_treeview_select(self, event = None):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]  # Get the ID of the selected item
        else:
            return
        selected_item = self.playlist_treeview.item(selected_item_id)
        hymn = self.controller.get_hymn_from_playlist(selected_item['values'])  # Get the selected item
        currently_playing = self.controller.is_playing()
        if not currently_playing and (hymn is None or not hymn.is_hymn):
            self.bpm_var.set("")
            self.bpm_entry.configure(state=tk.DISABLED)
            self.bpm_button.configure(state=tk.DISABLED)
            self.play_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.DISABLED)
            self.show_stop_selection_window_button.configure(state=tk.DISABLED)
            return
        self.bpm_entry.configure(state=tk.NORMAL)
        self.bpm_button.configure(state=tk.NORMAL)
        self.play_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.NORMAL)
        self.show_stop_selection_window_button.configure(state=tk.NORMAL)
        if not currently_playing:
            self.bpm_var.set(hymn.new_bpm)  # Set the bpm in the Entry

    def change_bpm(self):
        new_bpm = int(self.bpm_var.get())  # Get the new bpm from the entry
        self.controller.change_bpm(new_bpm)
        # Code to change the bpm goes here...

    def show_seperator_window(self, event=None):
        seperator_window = tk.Toplevel(self)
        seperator_window.title("Seperator Text")

        seperator_text = tk.StringVar(value="")
        seperator_entry = ttk.Entry(seperator_window, textvariable=seperator_text)
        seperator_entry.pack()
        submit_button = tk.Button(seperator_window, text="Submit", command=lambda : self.submit_seperator(seperator_text.get(), seperator_window))
        cancel_button = tk.Button(seperator_window, text="Cancel", command=lambda : seperator_window.destroy())
        submit_button.pack()
        cancel_button.pack()
        seperator_window.bind('<Return>', lambda event : self.submit_seperator(seperator_text.get(), seperator_window))
        seperator_window.bind('<Escape>', lambda : seperator_window.destroy())
        seperator_entry.focus_set()  # Set focus on the entry

    def submit_seperator(self, seperator_text, seperator_window):
        tag = "text"
        self.playlist_treeview.insert("", "end", values=("", seperator_text, ""), tags=(tag,))
        seperator_window.destroy()

    def move_up(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            index = self.playlist_treeview.index(selected_item)
            if index > 0:  # Ensure we're not already at the top
                self.playlist_treeview.move(selected_item, '', index - 1)
                # Update tags after moving
                for i, item in enumerate(self.playlist_treeview.get_children()):
                    if "text" not in self.playlist_treeview.item(item, "tags"):
                        self.playlist_treeview.item(item, tags=('oddrow' if i % 2 else 'evenrow'))

    def move_down(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            index = self.playlist_treeview.index(selected_item)
            # Ensure we're not already at the bottom
            if index < len(self.playlist_treeview.get_children()) - 1:
                self.playlist_treeview.move(selected_item, '', index + 1)
                # Update tags after moving
                for i, item in enumerate(self.playlist_treeview.get_children()):
                    if "text" not in self.playlist_treeview.item(item, "tags"):
                        self.playlist_treeview.item(item, tags=('oddrow' if i % 2 else 'evenrow'))

    def remove_from_playlist(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            self.playlist_treeview.delete(selected_item)
            # Update tags of all items below the deleted item
            for i, item in enumerate(self.playlist_treeview.get_children()):
                if "text" not in self.playlist_treeview.item(item, "tags"):
                  self.playlist_treeview.item(item, tags=('oddrow' if i % 2 else 'evenrow'))

    def show_loading_message(self):
        print("Loading", "The library files are still loading. Please wait.")


    def show_stop_selection_window(self):
        self.stop_selection_window = tk.Toplevel(self)
        self.stop_selection_window.title("Stop Selection")

        self.stop_buttons = []
        my_font = font.Font(family='Helvetica', size=12, weight='bold')

        stop_type_colors = {
            StopType.REED: "#8B0000",
         #   StopType.FLUTE: "green",  # Replace with the actual color for StopType.FLUTE
         #   StopType.STRING: "gold",
         #   StopType.PRINCIPAL: "blue"  # Replace with the actual color for StopType.STRING
            # Add more StopType values as needed...
        }

        for row, (manual_name, manual) in enumerate(manuals.items()):
            buttons = []
            frame = tk.LabelFrame(self.stop_selection_window, text=manual_name, padx=10, pady=10, borderwidth=2, relief=tk.GROOVE)
            for column, (_, stop) in enumerate(manual.stops.items()):
                color = stop_type_colors.get(stop.stop_type, "black")
                button = tk.Button(frame, text=stop.label_text, bg="gray", fg=color, width=8, height=4, font=my_font, autostyle=False)
                button.config(command=lambda btn=button, stp=stop: self.update_stop(stp, btn))
                button.grid(row=row, column=column, sticky="w")
                buttons.append(button)
            self.stop_buttons.append(buttons)
            frame.grid(row=row, column=0, sticky="w")

       # self.update_stop_selection_columns()

    def update_stop(self, stop, button):
        if button['bg'] == "gray":
            button['bg'] = "white"
            stop.is_engaged = True
        else:
            button['bg'] = "gray"
            stop.is_engaged = False
        self.send_button_states_to_controller()

    def send_button_states_to_controller(self):
        engaged_stops = []
        for row, (manual_name, manual) in enumerate(manuals.items()):
            for stop_name, stop in manual.stops.items():
                if stop.is_engaged:
                    engaged_stops.append(stop)
        self.controller.receive_engaged_stops(engaged_stops)

    def show_library_window(self):
        self.library_window.show()

    def transpose_check(self):
        transpose_state = self.transpose_check_state.get()
        self.controller.transpose_check(transpose_state)
        
    def set_controller(self, controller):
        self.controller = controller
        self.set_controller_dependencies()

    def set_controller_dependencies(self):
        self.filemenu.add_command(label="Load Playlist", command=self.controller.load_playlist)
        self.filemenu.add_command(label="Save Playlist", command=lambda: self.controller.save_playlist([self.playlist_treeview.item(item_id) for item_id in self.playlist_treeview.get_children()]))
        self.filemenu.add_separator()
        self.play_button.configure(command=lambda: self.play())
        self.stop_button.configure(command=self.controller.stop_playback)
        midi_devices = self.controller.get_midi_devices()
        for device in midi_devices:
            self.midi_menu.add_radiobutton(label=device, variable=self.selected_device, command=lambda: self.controller.set_midi_device(self.selected_device.get()))
        self.library_window = LibraryWindow(self, self.controller)

    def stop_loading(self, library_files):
        self.library_window.update_library_view(library_files)

    def play(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            values = self.playlist_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_playlist(values)
            if hymn is None:
                return
            self.controller.play_file(hymn, self.update_progress)

    def update_progress(self, value):
        self.section_progress_bar['value'] = value
        self.update_idletasks()

    def clear_playlist(self):
        self.playlist_treeview.delete(*self.playlist_treeview.get_children())

    def update_playlist(self, hymn):
        index = len(self.playlist_treeview.get_children())
        if hymn.is_hymn:
            tag = "oddrow" if index % 2 else "evenrow"
        else:
            tag = "text"
        self.playlist_treeview.insert("", "end", values=(hymn.hymn_number, hymn.title, hymn.abbreviated_titles), tags=(tag,))
        self.focus_playlist()

    def focus_playlist(self):
        self.playlist_treeview.focus_set()
        first_item = self.playlist_treeview.get_children()[0]
        self.playlist_treeview.focus(first_item)
        self.playlist_treeview.selection_set(first_item)

    def update_current_song(self, song):
        self.current_song.configure(text= song)

    def update_current_section(self, section):
        self.current_section.configure(text= section)

    def start_mainloop(self):
        tk.mainloop()

# You can include other related GUI classes and methods in this module as well.
