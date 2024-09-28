# view.py
import os
import sys
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from natsort import natsorted
from widgets import ScrolledTreeView, CreateToolTip, StopSelectionWindow, SongSelectionWindow
from config import kind_to_folder


if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

#pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

class ImportSongWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Import Song")
        self.controller = parent.controller
        self.parent = parent
        hymn = self.select_song_to_import()
        if hymn is None:
            return

        self.song_name_label = tk.Label(self, text="Song Name:")
        self.song_name_entry = tk.Entry(self)
        self.song_name_entry.insert(0, hymn.title)
        self.song_name_label.pack()
        self.song_name_entry.pack()

        self.liturgy_label = tk.Label(self, text="If song is part of the liturgy, use abbreviation to mark which, such as DS3 for Divine Service 3")
        self.liturgy_label.pack()
        self.song_number_label = tk.Label(self, text="Hymn Number")
        self.song_number_entry = tk.Entry(self)
        self.song_number_entry.insert(0, hymn.hymn_number)
        self.song_number_label.pack()
        self.song_number_entry.pack()

        self.track_name_label = tk.Label(self, text="Track Names:")
        self.track_name_label.pack()
        self.track_name_entries = []
        for _, name in enumerate(hymn.track_names.values()):
            entry = tk.Entry(self)
            entry.insert(0, name)
            entry.pack()
            self.track_name_entries.append(entry)

        self.classification_label = tk.Label(self, text="Classification:")
        self.classification_combobox = ttk.Combobox(self, values=list(kind_to_folder.keys()))
        self.classification_label.pack()
        self.classification_combobox.pack()

        self.import_button = ttk.Button(self, text="Import", command=lambda:self.import_song(hymn))
        self.import_button.pack()

    def select_song_to_import(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            _, _ , hymn, _ = self.controller.load_song(file_path)
            return hymn


    def import_song(self, hymn):
        song_number = self.song_number_entry.get()
        song_name = self.song_name_entry.get()
        track_names = {i+1: entry.get() for i, entry in enumerate(self.track_name_entries)}
        classification = self.classification_combobox.get()
        hymn.hymn_number = song_number
        hymn.title = song_name
        hymn.track_names = track_names
        hymn.kind = classification
        self.controller.add_hymn_to_library(hymn)
        self.parent.add_hymn_to_library(0, hymn)
        self.destroy()


class LibraryWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.stop_checkbuttons = []
        self.section_labels = []
        self.submit_button = None
        self.cancel_button = None

        self.parent_items = {}

        self.title("Library")
      #  self.geometry("500x800")
        self.minsize(120, 450)
        self.maxsize(1024, 600)

        container = ttk.Frame(self)
        container.pack(side="top", fill="both",padx=10, pady=10, expand=True)

        self.library_frame = tk.Frame(container, padx=10, pady=10)
        self.library_frame.pack_forget()

        self.library_treeview = ScrolledTreeView(self.library_frame, columns=("Number", "Title", "ParentTitle", "Kind", "Key", "TimeSignature"), show="tree headings", height=8)
        self.library_treeview.heading("Number", text="#", command=lambda: self.treeview_sort_column("Number"))
        self.library_treeview.heading("Title", text="Title", command=lambda: self.treeview_sort_column("Title"))
        self.library_treeview.heading("Kind", text="Kind", command=lambda: self.treeview_sort_column("Kind"))
        #self.library_treeview.heading("Key", text="Key", command=lambda: self.treeview_sort_column("Key", False))  # New column
        self.library_treeview.heading("TimeSignature", text="Time Signature", command=lambda: self.treeview_sort_column("TimeSignature"))  # New column
        self.library_treeview.column("Number", width=40, stretch="no")
        self.library_treeview.column("Title", stretch="yes", anchor="w")
        self.library_treeview.column("ParentTitle", width = 0, anchor="w")  # Text centered in column "ParentTitle"
        self.library_treeview.column("Kind", width = 50, stretch="no")
     #   self.library_treeview.column("Key", width = 40, stretch="no")  # New column
        self.library_treeview.column("TimeSignature", width=40, stretch="no")  # New column
        self.library_treeview.column("#0", width=0, stretch="no")
        self.library_treeview["displaycolumns"] = ("Number", "Title", "ParentTitle")  # Include new columns
        self.filter_label = tk.Label(self, text="Filter Text")
        self.filter_entry = ttk.Entry(self, width=50)
        self.filter_entry.bind('<KeyRelease>', self.filter_treeview)
        self.add_button = ttk.Button(self, text="Add to Playlist", command=self.add_to_playlist)
        self.edit_button = ttk.Button(self, text="Edit Song Defaults", command=self.edit_song)
        self.progress = ttk.Progressbar(container, orient="horizontal", length=200, mode="determinate")
        self.progress.place(relx=0.5, rely=0.45, anchor='center')
        self.library_treeview.bind("<Double-1>", lambda _: self.add_to_playlist())
        self.loading_label = tk.Label(container, text="Refreshing library...")
        self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
        self.menu_bar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.filemenu)
        self.config(menu=self.menu_bar)
      #  self.filemenu.add_command(label="Refresh Library", command=self.refresh_library)
        self.filemenu.add_command(label="Import Song", command=self.import_song)

        # self.foo = ttk.Frame(container)
        # ttk.Label(self.foo, text="Add Full Divine Service Settings").pack()
        # DS1 = ttk.Button(self.foo, text="Add DS1", command=lambda: self.add_ds_setting("DS1"))
        # DS2 = ttk.Button(self.foo, text="Add DS2", command=lambda: self.add_ds_setting("DS2"))
        # DS3 = ttk.Button(self.foo, text="Add DS3", command=lambda: self.add_ds_setting("DS3"))
        # #self.foo.DS4 = ttk.Button(self.foo, text="Add DS4", command=lambda: self.add_ds_setting("DS4"))
        # #self.foo.DS5 = ttk.Button(self.foo, text="Add DS5", command=lambda: self.add_ds_setting("DS5"))
        # DS1.pack()
        # DS2.pack()
        # DS3.pack()
        
        # self.foo.pack(side="left", fill="y", expand=True)

        self.controller.load_library_files(reloadCache=False, total_files_callback=self.set_total_files, update_progress_callback=self.update_progress)
        self.withdraw()  # Hide the window until the library is loaded
        self.protocol('WM_DELETE_WINDOW', self.hide)
        
    def import_song(self):
        self.import_song_window = ImportSongWindow(self)

    def filter_treeview(self, event=None):
        phrase = self.filter_entry.get()
        for i in self.library_treeview.get_children():
            self.library_treeview.delete(i)
        self.parent_items.clear()
        hymn_list = {}
        for hymn in self.controller.get_library().values():
            if phrase.lower() in hymn.title.lower() or phrase.lower() in hymn.hymn_number.lower():
                hymn_list[f"{hymn.hymn_number}-{hymn.title}"] = hymn
        self.update_library_view(hymn_list)

    def edit_song(self):
        selected_item = self.library_treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]
            values = self.library_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_library(values)
            if hymn is None:
                return
            song_selection_window = SongSelectionWindow(self.master, self.controller, hymn, "library_edit")
            updated_hymn = song_selection_window.onClose()
            if updated_hymn is not None:
                self.controller.update_library_hymn(updated_hymn, selected_item_id)

    def add_to_playlist(self):
        selected_items = self.library_treeview.selection()
        for selected_item in selected_items:
            values = self.library_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_library_to_playlist(values)
            if hymn is None:
                continue
            # Make the change here
            song_selection_window = SongSelectionWindow(self.master, self.controller, hymn, "add_to_playlist")
            hymn = song_selection_window.onClose()
            if hymn is not None:
                self.controller.add_to_playlist(hymn)

    def set_total_files(self, total):
        self.progress['maximum'] = total

    def update_progress(self, value):
        self.progress['value'] = value
        self.update_idletasks()

    def show_library_frame(self):
        self.treeview_sort_column("Number", "Title")
        self.library_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.filter_label.pack(side=tk.TOP, fill="x", expand=False)
        self.filter_entry.pack(side=tk.TOP, fill="x", expand=False, pady=(0, 20))
        self.add_button.pack(side=tk.RIGHT, padx=(0, 40), pady=(0, 20))
        self.edit_button.pack(side=tk.RIGHT, padx=(0, 40), pady=(0, 20))
        self.loading_label.destroy()
        self.progress.destroy()

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()  # Show the window

    def treeview_sort_column(self, col1, col2=None, reverse=False):
        for parent in self.library_treeview.get_children(''):
            if col2:
                data = [(self.library_treeview.set(child, col1), self.library_treeview.set(child,col2), child) for child in self.library_treeview.get_children(parent)]
                data = natsorted(data, key=lambda x: (x[0],x[1]), reverse=reverse)
            else:
                data = [(self.library_treeview.set(child, col1), child) for child in self.library_treeview.get_children(parent)]
                data = natsorted(data, key=lambda x: x[0], reverse=reverse)

            for index, item in enumerate(data):
                if col2:
                    _,_,k = item
                else:
                    _,k = item
                self.library_treeview.move(k, parent, index)
                # Update the tags for the rows after sorting
                tag = "oddrow" if index % 2 else "evenrow"
                self.library_treeview.item(k, tags=(tag,))

        self.library_treeview.heading(col1, command=lambda: self.treeview_sort_column(col1,col2, not reverse))


    def start_loading(self):
        self.library_treeview.pack_forget()
        self.loading_label.pack()

    def update_library_view(self, hymns):
        for i, hymn in enumerate(hymns.values()):
            self.add_hymn_to_library(i, hymn)


    def add_hymn_to_library(self, i, hymn):
        if hymn.path:
            tag = "oddrow" if i % 2 else "evenrow"
        else:
            tag = "notFound"
        #print(f"Adding hymn: {hymn.hymn_number}, kind: {hymn.kind}, path: {hymn.path}")
        #print(f"Current parent items: {self.parent_items}")

        if hymn.kind == "DivineService":
            if hymn.hymn_number not in self.parent_items:
                setting_number = hymn.hymn_number.replace("DS", "Setting ")
                #print(f"Creating new parent item for hymn number: {hymn.hymn_number}")
                self.parent_items[hymn.hymn_number] = self.library_treeview.insert("", "end", values=("", setting_number, "", "", "", ""), tags=("parent",))
                self.library_treeview.item(self.parent_items[hymn.hymn_number], open=True)
                self.library_treeview.insert(self.parent_items[hymn.hymn_number], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
            else:
                setting_number = hymn.hymn_number.replace("DS", "Setting ")
                #print(f"Adding hymn to existing parent item for hymn number: {hymn.hymn_number}")
                self.library_treeview.insert(self.parent_items[hymn.hymn_number], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
        else:
            if hymn.kind not in self.parent_items:
                #print(f"Creating new parent item for hymn kind: {hymn.kind}")
                self.parent_items[hymn.kind] = self.library_treeview.insert("", "end", values=("", f"{hymn.kind}", "", "", "", ""), tags=("parent",))
                self.library_treeview.item(self.parent_items[hymn.kind], open=True)
                self.library_treeview.insert(self.parent_items[hymn.kind], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))
            else:
                #print(f"Adding hymn to existing parent item for hymn kind: {hymn.kind}")
                self.library_treeview.insert(self.parent_items[hymn.kind], "end", values=(hymn.hymn_number, hymn.title, "", hymn.kind, hymn.key_signature, f"{hymn.time_signature['numerator']}/{hymn.time_signature['denominator']}"), tags=(tag,))


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
        self.maxsize(1024, 600)
        self.resizable(0,  0)
        self.title("AutoBach Organ Player")
        self.configure(relief="ridge")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=10)
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
        self.button_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.button_frame.master.columnconfigure(1, minsize=190, weight=1)

        # Create the buttons
        self.add_button = ttk.Button(self.button_frame, text="Show Library",  command=self.show_library_window)
        self.add_text = ttk.Button(self.button_frame, text="Add Text", command=self.show_seperator_window)
        self.remove_button = ttk.Button(self.button_frame, text="Remove from Playlist", command=self.remove_from_playlist)
        self.edit_button = ttk.Button(self.button_frame, text="Edit Song", command=self.edit_playlist_item)
        self.move_up_button = ttk.Button(self.button_frame, text="Move Item Up", command=self.move_up)
        self.move_down_button = ttk.Button(self.button_frame, text="Move Item Down", command=self.move_down)

        # # Add the buttons to the frame
        for i in range(10):
            self.button_frame.grid_rowconfigure(i, weight=1)

        # Add the buttons to the frame
        self.add_button.grid(row=1, column=0, sticky="nsew", pady=(28, 3))
        CreateToolTip(self.add_button, "Show library to add songs to the playlist")
        self.remove_button.grid(row=2, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.remove_button, "Remove a song from the playlist")
        self.add_text.grid(row=3, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.add_text, "Add a text seperator to the playlist")
        self.edit_button.grid(row=4, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.edit_button, "Edit a song in the playlist, this only changes the song for this playlist")
        self.move_up_button.grid(row=5, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.move_up_button, "Move a song up in the playlist")
        self.move_down_button.grid(row=6, column=0, sticky="nsew", pady=3)
        CreateToolTip(self.move_down_button, "Move a song down in the playlist")

        self.right_frame = tk.Frame(container)
        self.right_frame.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=10, pady=20)
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
        self.stop_button = ttk.Button(self.button_grid, bootstyle=DANGER, state=tk.DISABLED, text='''Stop''', padding=(20,10))
        self.play_button = ttk.Button(self.button_grid, bootstyle=SUCCESS, state=tk.DISABLED,  text='''Play''', padding=(20,10))

        self.bpm_var = tk.StringVar()  # Holds the value of the bpm entry
        self.bpm_entry = ttk.Entry(self.control_Frame, state=tk.DISABLED, textvariable=self.bpm_var)
        self.show_stop_selection_window_button = ttk.Button(self.control_Frame, text="Show Stop Selection Window", command=self.show_stop_selection_window, padding=(5,20))    
        self.bpm_button = ttk.Button(self.control_Frame, text="Change bpm", bootstyle=INFO, state=tk.DISABLED, command=self.change_bpm)

        self.control_Frame.grid(row=2, column=0, sticky="nswe")  # Use grid instead of pack
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

    def show_stop_selection_window(self):
        StopSelectionWindow(self.master, None, self.controller, None, context="playlist")

    def edit_playlist_item(self):
        """
        Edit the selected item in the playlist.
        """
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]
            hymn = self.controller.get_hymn_from_playlist(
                self.playlist_treeview.item(selected_item_id)['values']
            )
            if hymn is None:
                return
            song_selection_window = SongSelectionWindow(self, self.controller, hymn, "playlist")
            updated_hymn = song_selection_window.onClose()
            if updated_hymn is not None:
                self.controller.remove_from_playlist(hymn)
                self.controller.update_playlist_hymn(updated_hymn, selected_item_id)
        else:
            return

    def on_treeview_select(self, event = None):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]  # Get the ID of the selected item
        else:
            return
        selected_item = self.playlist_treeview.item(selected_item_id)
        hymn = self.controller.get_hymn_from_playlist(selected_item['values'])  # Get the selected item
        currently_playing = self.controller.is_playing()
        if not currently_playing and (hymn is None or not hymn.is_hymn or hymn.path is None):
            self.bpm_var.set("")
            self.bpm_entry.configure(state=tk.DISABLED)
            self.bpm_button.configure(state=tk.DISABLED)
            self.play_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.DISABLED)
            self.bpm_entry.configure(state=tk.DISABLED)
            self.show_stop_selection_window_button.configure(state=tk.DISABLED)
            return
        self.bpm_entry.configure(state=tk.NORMAL)
        self.bpm_button.configure(state=tk.NORMAL)
        self.play_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.NORMAL)
        self.bpm_entry.configure(state=tk.NORMAL)
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
        seperator_window.attributes('-topmost', True)  # Ensure the window stays on top

        # Get the coordinates of the previous window
        previous_window_x = self.winfo_x()
        previous_window_y = self.winfo_y()
        previous_window_width = self.winfo_width()
        previous_window_height = self.winfo_height()

        # Calculate the position for the new window
        new_window_x = previous_window_x + (previous_window_width // 2)
        new_window_y = previous_window_y + (previous_window_height // 2)
        # Set the position of the new window
        seperator_window.geometry(f"+{new_window_x}+{new_window_y}")

        seperator_text = tk.StringVar(value="")
        seperator_entry = ttk.Entry(seperator_window, textvariable=seperator_text)
        seperator_entry.pack()
        submit_button = tk.Button(seperator_window, text="Submit", command=lambda : self.submit_seperator(seperator_text.get(), seperator_window))
        cancel_button = tk.Button(seperator_window, text="Cancel", command=lambda : seperator_window.destroy())
        submit_button.pack()
        cancel_button.pack()
        seperator_window.bind('<Return>', lambda event : self.submit_seperator(seperator_text.get(), seperator_window))
        seperator_window.bind('<Escape>', lambda event : seperator_window.destroy())
        seperator_entry.focus_set()  # Set focus on the entry

    def submit_seperator(self, seperator_text, seperator_window):
        tag = "text"
        self.playlist_treeview.insert("", "end", values=("", seperator_text, ""), tags=(tag,))
        seperator_window.destroy()

    def update_playlist_tags(self):
        for i, item in enumerate(self.playlist_treeview.get_children()):
            if "text" not in self.playlist_treeview.item(item, "tags"):
                self.playlist_treeview.item(item, tags=('oddrow' if i % 2 else 'evenrow'))

    def move_up(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            index = self.playlist_treeview.index(selected_item)
            if index > 0:  # Ensure we're not already at the top
                self.playlist_treeview.move(selected_item, '', index - 1)
                # Update tags after moving
                self.update_playlist_tags()

    def move_down(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            index = self.playlist_treeview.index(selected_item)
            # Ensure we're not already at the bottom
            if index < len(self.playlist_treeview.get_children()) - 1:
                self.playlist_treeview.move(selected_item, '', index + 1)
                # Update tags after moving
                self.update_playlist_tags()

    def remove_from_playlist(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            values = self.playlist_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_playlist(values)
            if hymn is not None:
                self.controller.remove_from_playlist(hymn)         
            self.playlist_treeview.delete(selected_item)
            # Update tags of all items below the deleted item
            self.update_playlist_tags()

    def show_loading_message(self):
        print("Loading", "The library files are still loading. Please wait.")

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
        self.filemenu.add_command(label="Save Playlist", command=self.save_playlist)
        self.filemenu.add_command(label="Clear Playlist", command=self.clear_playlist)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.midi_menu.add_command(label="Refresh Midi Devices", command=self.refresh_midi_devices)
        self.midi_menu.add_separator()
        self.play_button.configure(command=self.play)
        self.stop_button.configure(command=self.controller.stop_playback)
        self.library_window = LibraryWindow(self, self.controller)

    def save_playlist(self):
        playlist = [self.playlist_treeview.item(item_id) for item_id in self.playlist_treeview.get_children()]
        self.controller.save_playlist(playlist)
    
    def clear_playlist(self):
        self.controller.clear_playlist()
        self.playlist_treeview.delete(*self.playlist_treeview.get_children())

    def refresh_midi_devices(self):
        self.midi_menu.delete(2, 'end')
        midi_devices = self.controller.get_midi_devices()
        for device in midi_devices:
            self.midi_menu.add_radiobutton(label=device, variable=self.selected_device, command=self.set_midi_device)

    def set_midi_device(self):
        self.controller.set_midi_device(self.selected_device.get())

    def stop_loading(self, library_files):
        self.library_window.update_library_view(library_files)
        self.library_window.show_library_frame()


    def play(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            values = self.playlist_treeview.item(selected_item, "values")
            hymn = self.controller.get_hymn_from_playlist(values)
            if hymn is None:
                return
            self.controller.play_file(hymn, self.update_progress)

    def select_next_item(self):
        selected_item = self.playlist_treeview.selection()
        if selected_item:
            # Get the index of the current selection
            current_index = self.playlist_treeview.index(selected_item)
            # Get the total number of items
            total_items = len(self.playlist_treeview.get_children())
            # If the current selection is not the last item, select the next item
            if current_index < total_items - 1:
                next_item = self.playlist_treeview.get_children()[current_index + 1]
                self.playlist_treeview.selection_set(next_item)
                values = self.playlist_treeview.item(next_item, "values")
                hymn = self.controller.get_hymn_from_playlist(values)
                if hymn is None:
                    return
                if hymn.is_prelude:
                    self.controller.play_file(hymn, self.update_progress)

    def update_progress(self, value):
        self.section_progress_bar['value'] = value
        self.update_idletasks()

    def clear_playlist(self):
        self.playlist_treeview.delete(*self.playlist_treeview.get_children())

    def update_playlist_item(self, hymn, index):
        self.playlist_treeview.item(index, values=(hymn.hymn_number, hymn.title, hymn.abbreviated_titles))

    def update_playlist(self, hymn):
        children = self.playlist_treeview.get_children()
        index = len(children)
        last_text_index = next((i for i, item in reversed(list(enumerate(children))) if "text" in self.playlist_treeview.item(item, "tags")), -1)
        if hymn.is_hymn:
            if hymn.path:
                tag = "oddrow" if (index - (last_text_index + 1)) % 2 else "evenrow"
            else:
                tag = "notFound"
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
