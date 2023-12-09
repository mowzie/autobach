import os
import queue
import threading
from tkinter import filedialog, messagebox
import tkinter
import time
from MidoAdd import MidiFile
from Stops2 import DefaultSettings

PLAYLISTSAVESPATH = os.path.join(os.path.dirname(__file__), "PlaylistSaves")


class OrganPlayerController:
    def __init__(self, model, view):
        self.model = model
        self.library_controller = LibraryController(model, view)
        self.playlist_controller = PlaylistController(model, view)
        self.playback_controller = PlaybackController(model, view)

    def is_playing(self):
        return self.playback_controller.is_playing

    def receive_engaged_stops(self, engaged_stops):
        self.playback_controller.receive_engaged_stops(engaged_stops)

    def transpose_check(self, transpose):
        self.playback_controller.transpose_check(transpose)

    def play_file(self, hymn, update_progress_callback):
        if not hymn.is_hymn:
            return
        self.playback_controller.play_file(hymn, update_progress_callback)

    def change_bpm(self, bpm):
        self.playback_controller.change_bpm(bpm)

    def stop_playback(self):
        self.playback_controller.stop_playback()

    def get_hymn_from_playlist(self, values):
        return self.playlist_controller.get_hymn_from_playlist(values)

    def load_playlist(self):
        self.playlist_controller.load_playlist()

    def save_playlist(self, playlist):
        self.playlist_controller.save_playlist(playlist)

    def add_to_playlist(self, selected_hymn):
        self.playlist_controller.add_to_playlist(selected_hymn)

    def get_hymn_from_library(self, item):
        return self.library_controller.get_hymn_from_library(item)

    def load_library_files(self, reloadCache = False, total_files_callback = None, update_progress_callback=None):
        self.library_controller.load_library_files(reloadCache = reloadCache,total_files_callback = total_files_callback, update_progress_callback=update_progress_callback)

    def get_default_stops(self):
        return DefaultSettings().get_default_stops()

    def get_default_stops_and_channels(self):
        return DefaultSettings().get_default_stops_and_channels()

    def get_midi_devices(self):
        return self.model.get_midi_devices()

    def save_library(self):
        self.model.save_library()

class LibraryController:
    def __init__(self, model, view):
        self.model = model
        self.library_files = None
        self.loading_done = threading.Event()
        self.view = view

    def load_library_files(self, reloadCache = False, total_files_callback = None, update_progress_callback=None):
        def task(callback, total_files_callback, update_progress_callback):
            def update_progress_callback(value):
                self.view.library_window.update_progress(value)

            self.library_files = self.model.refresh_library_thread(reloadCache ,total_files_callback, update_progress_callback)
            self.loading_done.set()
            self.view.library_window.show_library_frame()

            callback(self.library_files)
        # TODO: move this to the model to update the view
        threading.Thread(target=task, args=(self.view.stop_loading,total_files_callback, update_progress_callback,)).start() 

    def show_library_window(self):
        """
        Show the library window.

        If loading is not done, show a loading message.
        Otherwise, show the library window with the loaded library files.
        """
        if not self.loading_done.is_set():
            self.view.show_loading_message()
        else:
            self.view.show_library_window(self.library_files)

    def get_library(self):
        """
        Get the library.

        Returns:
            The library object.
        """
        return self.model.library

    def get_hymn_from_library(self, item):
        return self.model.get_hymn_from_library(item)

    def save_library(self):
        self.model.save_library("cache.json", self.model.library)

class PlaylistController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def load_playlist(self):
        if not os.path.exists(PLAYLISTSAVESPATH):
            os.mkdir(PLAYLISTSAVESPATH)
        filename = filedialog.askopenfilename(filetypes=[('JSON files', '*.json')], initialdir=PLAYLISTSAVESPATH)
        if filename:
            self.view.clear_playlist()
            hymns = self.model.load_playlist(filename)
            for hymn in hymns:
                self.view.update_playlist(hymn)

    def save_playlist(self, playlist):
        if not os.path.exists(PLAYLISTSAVESPATH):
            os.mkdir(PLAYLISTSAVESPATH)
        filename = tkinter.filedialog.asksaveasfilename(initialfile="playlist.json",  filetypes=[('JSON files', '*.json')], defaultextension=".json", initialdir=PLAYLISTSAVESPATH)
        if filename:
            self.model.save_playlist(playlist, filename)

    def add_to_playlist(self, selected_hymn):
        hymn = selected_hymn
        sorted_markers, abbreviated_titles = self.sort_markers_and_get_abbreviated_titles(hymn.selected_markers)
        hymn.selected_markers = sorted_markers
        hymn.abbreviated_titles = abbreviated_titles
        self.model.add_to_playlist(hymn)
        # TODO: Move this to the model
        self.view.update_playlist(hymn)

    def sort_markers_and_get_abbreviated_titles(self, markers):
        sorted_markers = sorted(markers, key=self.custom_sort)
        abbreviated_titles = ", ".join(self.model.get_short_titles(sorted_markers))
        return sorted_markers, abbreviated_titles

    def custom_sort(self, x):
        title = x.title
        if title.startswith("Intro"):
            return 0
        elif title.startswith("Verse"):
            return int(title.lstrip("Verse"))
        else:
            return float('inf')  # This will always sort "Amen" last

    def get_hymn_from_playlist(self, values):
        return self.model.get_hymn_from_playlist(values)

class PlaybackController:
    """
    The PlaybackController class handles the playback of MIDI files and controls various aspects of the playback process.

    Attributes:
        model (Model): The model object that provides access to the MIDI device and other functionalities.
        view (View): The view object that handles the user interface.
        stop_thread (threading.Event): An event used to signal the playback thread to stop.
        stop_progressthread (threading.Event): An event used to signal the progress bar thread to stop.
        midi_device (str): The MIDI device name.
        is_playing (bool): Indicates whether a MIDI file is currently being played.
        transpose_queue (queue.Queue): A queue used to store transpose values.
        sysex_queue (queue.Queue): A queue used to store SysEx messages.
        bpm_queue (queue.Queue): A queue used to store BPM values.
        transpose (int): The transpose value for MIDI notes.
        current_time (float): The current playback time in seconds.
        scaler (float): The scaler value used to adjust the playback speed.
    """

    def __init__(self, model, view):
        """
        Initializes a new instance of the PlaybackController class.

        Args:
            model (Model): The model object that provides access to the MIDI device and other functionalities.
            view (View): The view object that handles the user interface.
        """
        self.model = model
        self.stop_thread = threading.Event()
        self.stop_progressthread = threading.Event()
        self.midi_device = None
        self.is_playing = False
        self.transpose_queue = queue.Queue()
        self.sysex_queue = queue.Queue()
        self.bpm_queue = queue.Queue()
        self.view = view
        self.transpose = 0
        self.current_time = 0.0
        self.scaler = 1.0

    def play_file(self, hymn, update_progress_callback):
        """
        Plays a MIDI file.

        Args:
            hymn (Hymn): The hymn object representing the MIDI file to be played.
            update_progress_callback (callable): A callback function to update the progress bar.

        Returns:
            None
        """
        if self.is_playing:
            return
        if self.midi_device is None:
            self.midi_device = self.model.get_midi_device()
        self.view.update_current_song(hymn.title)
        self.is_playing = True
        self.stop_thread.clear()
        threading.Thread(target=self.__playback_thread, args=(hymn, update_progress_callback)).start()

    def progressbar_thread(self, update_progress_callback, duration):
        """
        The thread function that updates the progress bar.

        Args:
            update_progress_callback (callable): A callback function to update the progress bar.
            duration (float): The duration of the current section in seconds.

        Returns:
            None
        """
        self.stop_progressthread.clear()
        self.scaled_time = 0.0
        print(f"duration: {duration}")
        print(f"scaler: {self.scaler}")
        start_time = time.perf_counter()
        while not self.stop_progressthread.is_set():
            current_time = time.perf_counter()
            elapsed_time = current_time - start_time
            if elapsed_time >= 0.01:
                self.scaled_time += 0.01 * self.scaler
                update_progress_callback((self.scaled_time / duration) * 100)
                start_time = current_time

    def __playback_thread(self, hymn, update_progress_callback):
        """
        The thread function that handles the playback of the MIDI file.

        Args:
            hymn (Hymn): The hymn object representing the MIDI file to be played.
            update_progress_callback (callable): A callback function to update the progress bar.

        Returns:
            None
        """
        outport = self.model.open_midi_output(self.midi_device)
        transpose = 0
        base_bpm = hymn.bpm
        track_names = {int(k): v for k, v in hymn.track_names.items()}

        for marker in hymn.selected_markers:
            real_duration = marker.stop_time - marker.start_time
            self.stop_progressthread.set()
            time.sleep(0.05)

            self.view.update_current_section(marker.title)
            self.handle_sysex_messages(outport, marker.stops)
            step = 0

            midi = MidiFile(filename = hymn.path)

            if base_bpm != hymn.new_bpm:
                self.scaler = int(hymn.new_bpm) / int(base_bpm)
            else:
                self.scaler = 1.0
            MidiFile.set_bpm_scaler(midi, self.scaler)

            if self.stop_thread.is_set():
                break
            threading.Thread(target=self.progressbar_thread, args=(update_progress_callback, real_duration)).start()

            for (msg, acc_time) in midi.play(starting_timestamp=marker.start_time, ending_timestamp=marker.stop_time):
               # self.scaled_time = acc_time
                if self.stop_thread.is_set():
                    break
                self.handle_bpm_changes(midi, base_bpm)
                self.handle_transpose_changes(outport, transpose)
                self.handle_note_messages(msg, track_names, transpose, step, outport)
                step += 1
            self.stop_progressthread.set()
            #self.model.reset_midi_output(outport)

        self.stop_progressthread.set()
        self.model.reset_midi_output(outport)
        self.model.close_midi_output(outport)
        self.view.update_current_section("")
        self.view.update_current_song("")
        self.is_playing = False

    def handle_sysex_messages(self, outport, stops):
        """
        Handles the SysEx messages for the engaged stops.

        Args:
            outport (mido.ports.Output): The MIDI output port.
            stops (list): The list of engaged stops.

        Returns:
            None
        """
        if stops != []:
            sysex_string = self.model.stops_to_sysex(stops)
            msg = self.model.sysex_to_mido(sysex_string)
         #   print(sysex_string)
         #   print(msg)
            self.model.send_midi_message(msg, outport)

    def handle_bpm_changes(self, midi, base_bpm):
        """
        Handles the BPM changes during playback.

        Args:
            midi (mido.MidiFile): The MIDI file object.
            base_bpm (int): The base BPM value of the MIDI file.

        Returns:
            None
        """
        if not self.bpm_queue.empty():
            new_bpm = self.bpm_queue.get()
            self.scaler = int(new_bpm) / int(base_bpm)
            MidiFile.set_bpm_scaler(midi, self.scaler)

    def handle_transpose_changes(self, outport, transpose):
        """
        Handles the transpose changes during playback.

        Args:
            outport (mido.ports.Output): The MIDI output port.
            transpose (int): The transpose value.

        Returns:
            None
        """
        if not self.transpose_queue.empty():
            outport.reset()
            transpose = self.transpose_queue.get()
            if transpose == 1:
                transpose = 12

    def handle_note_messages(self, msg, track_names, transpose, step, outport):
        """
        Handles the note messages during playback.

        Args:
            msg (mido.Message): The MIDI message.
            track_names (dict): The dictionary mapping track numbers to track names.
            transpose (int): The transpose value.
            step (int): The current step number.
            outport (mido.ports.Output): The MIDI output port.

        Returns:
            None
        """
        if msg.type == 'end_of_track':
            self.stop_thread.set()
            return
        elif msg.is_meta or msg.type in ['control_change', 'program_change', 'sysex']:
            return
        if msg.type in ['note_on', 'note_off']:
            try:
                new_msg = msg.copy()
                new_msg.channel = track_names[msg.channel+1]
            except KeyError:
                return
            if transpose != 0:
                new_msg.note += transpose
           # print("step " + str(step), new_msg.type, str(new_msg))
            self.model.send_midi_message(new_msg, outport)

    def stop_playback(self):
        """
        Stops the playback.

        Returns:
            None
        """
        self.stop_thread.set()

    def receive_engaged_stops(self, engaged_stops):
        """
        Receives the engaged stops and sends the corresponding SysEx message.

        Args:
            engaged_stops (list): The list of engaged stops.

        Returns:
            None
        """
        # Convert the engaged stops to a SysEx string
        sysex_string = self.model.stops_to_sysex(engaged_stops)

        # Convert the SysEx string to a mido.Message
        msg = self.model.sysex_to_mido(sysex_string)

        # Print the SysEx string and the mido.Message for debugging
      #  print(sysex_string)
      #  print(msg)

        if self.is_playing:
            # If the organ is playing, add the message to the queue
            self.sysex_queue.put(msg)
        else:
            # If the organ is not playing, send the message immediately
            self.model.send_midi_message(msg)


    def transpose_check(self, transpose):
        """
        Checks if the transpose value has changed and updates the transpose queue.

        Args:
            transpose (int): The new transpose value.

        Returns:
            None
        """
        if self.transpose != transpose:
            self.transpose = transpose
            self.transpose_queue.put(transpose)

    def change_bpm(self, bpm):
        """
        Changes the BPM value.

        Args:
            bpm (int): The new BPM value.

        Returns:
            None
        """
        int_bpm = int(bpm)
        # if int_bpm < 60 or int_bpm > 200:
        #     messagebox.showerror("Error", "bpm must be between 60 and 200")
        #     return
        self.bpm_queue.put(int_bpm)
