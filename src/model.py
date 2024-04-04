# model.py

import ctypes
import json
import multiprocessing
import os
import sys
import time
import concurrent.futures
import mido
import mido.backends.rtmidi
import shutil
from config import kind_to_folder
from Stops2 import *

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

#pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

class PlaylistHymn:
    """
    Represents a hymn in the playlist.

    Attributes:
        title (str): The title of the hymn.
        hymn_number (str): The number of the hymn.
        path (str): The path of the hymn.
        kind (str): The kind of the hymn.
        is_hymn (bool): Indicates if the item is a hymn.
        markers (list): List of markers.
        selected_markers (list): List of selected markers.
        track_channels (dict): Dictionary of track channels.
        track_names (dict): Dictionary of track names.
        time_signature (dict): Dictionary of time signatures.
        bpm (int): Beats per minute.
        new_bpm (int): New beats per minute.
        abbreviated_titles (str): Abbreviated titles of the hymn.
    """

    def __init__(self, title, hymn_number, path, kind, is_hymn=True, markers=None, selected_markers=None, track_channels=None, track_names=None, time_signature=None, bpm=120, new_bpm=0, abbreviated_titles=""):
        self.title = title
        self.hymn_number = hymn_number
        self.path = path
        self.kind = kind
        self.is_hymn = is_hymn
        self.markers = markers or []
        self.selected_markers = selected_markers or []
        self.track_channels = track_channels or {}  # Attribute for the tracks
        self.track_names = track_names or {}  # New attribute for the track channels
        self.time_signature = time_signature or {}
        self.bpm = bpm
        self.new_bpm = bpm if new_bpm == 0 else new_bpm
        self.abbreviated_titles = abbreviated_titles
        self.is_prelude = False

    @classmethod
    def from_library_hymn(cls, library_hymn):
        """
        Creates a PlaylistHymn object from a LibraryHymn object.

        Args:
            library_hymn (LibraryHymn): The LibraryHymn object.

        Returns:
            PlaylistHymn: The created PlaylistHymn object.
        """
        return cls(
            title=library_hymn.title,
            hymn_number=library_hymn.hymn_number,
            path=library_hymn.path,
            kind=library_hymn.kind,
            is_hymn=library_hymn.is_hymn,
            markers=library_hymn.markers,
            # selected_markers=library_hymn.selected_markers,
            track_channels=library_hymn.track_channels,
            track_names=library_hymn.track_names,
            time_signature=library_hymn.time_signature,
            bpm=library_hymn.bpm,
            new_bpm=library_hymn.new_bpm,
            # abbreviated_titles=library_hymn.abbreviated_titles
        )

    def to_dict(self, index):
        """
        Converts the PlaylistHymn object to a dictionary.

        Args:
            index (int): The index of the hymn.

        Returns:
            dict: The dictionary representation of the PlaylistHymn object.
        """
        key = f"{self.hymn_number}-{self.title}-{self.abbreviated_titles}-{index}"
        return {
            key: {
                'title': self.title,
                'hymn_number': self.hymn_number,
                'path': self.path,
                'kind': self.kind,
                'is_hymn': self.is_hymn,
                'markers': [marker.to_dict() for marker in self.markers],
                'selected_markers': [marker.to_dict() for marker in self.selected_markers],
                'track_channels': self.track_channels,
                'track_names': self.track_names,
                'time_signature': self.time_signature,
                'bpm': self.bpm,
                'new_bpm': self.new_bpm
            }
        }

    @staticmethod
    def dict_to_hymn(dictionary):
        """
        Converts a dictionary to a PlaylistHymn object.

        Args:
            dictionary (dict): The dictionary representation of the PlaylistHymn object.

        Returns:
            PlaylistHymn: The created PlaylistHymn object.
        """
        key = list(dictionary.keys())[0]
        dictionary = dictionary[key]
        markers = [Marker(**marker_dict) for marker_dict in dictionary.get('markers', [])]
        selected_markers = [Marker(**marker_dict) for marker_dict in dictionary.get('selected_markers', [])]
        track_names = dictionary.get('track_names', {})
        track_names = {int(k): v for k, v in track_names.items()}

        return PlaylistHymn(
            title=dictionary['title'],
            hymn_number=dictionary['hymn_number'],
            path = dictionary['path'] if os.path.isfile(dictionary['path']) else None,
            kind=dictionary['kind'],
            is_hymn=dictionary['is_hymn'],
            markers=markers,
            selected_markers=selected_markers,
            track_channels=dictionary.get('track_channels', {}),
            track_names=track_names,
            time_signature=dictionary.get('time_signature', {}),
            bpm=dictionary.get('bpm', 120),
            new_bpm=dictionary.get('new_bpm'),
            abbreviated_titles=key.split("-")[-2]
        )

class LibraryHymn:
    """
    Represents a hymn in the library.

    Attributes:
        title (str): The title of the hymn.
        hymn_number (str): The number of the hymn.
        path (str): The path of the hymn.
        kind (str): The kind of the hymn.
        is_hymn (bool): Indicates if the item is a hymn.
        markers (list): List of markers.
        track_channels (dict): Dictionary of track channels.
        track_names (dict): Dictionary of track names.
        key_signature (str): The key signature of the hymn.
        time_signature (dict): Dictionary of time signatures.
        bpm (int): Beats per minute.
        new_bpm (int): New beats per minute.
    """

    def __init__(self, title, hymn_number, path, kind, is_hymn=True, markers=None, track_channels=None, track_names=None, key_signature=None, time_signature=None, bpm=120, new_bpm=0):
        self.title = title
        self.hymn_number = hymn_number
        self.path = path
        self.kind = kind
        self.is_hymn = is_hymn
        self.markers = markers or []
        self.track_channels = track_channels or {}  # Attribute for the tracks
        self.track_names = track_names or {}
        self.time_signature = time_signature or {}
        self.key_signature = key_signature
        self.bpm = bpm
        self.new_bpm = bpm if new_bpm == 0 else new_bpm

    def to_dict(self):
        """
        Converts the LibraryHymn object to a dictionary.

        Returns:
            dict: The dictionary representation of the LibraryHymn object.
        """
        return {
            'title': self.title,
            'hymn_number': self.hymn_number,
            'path': self.path,
            'kind': self.kind,
            'is_hymn': self.is_hymn,
            'markers': [marker.to_dict() for marker in self.markers],
            'track_channels': self.track_channels,
            'track_names': self.track_names,
            'time_signature': self.time_signature,
            'key_signature': self.key_signature,
            'bpm': self.bpm,
            'new_bpm': self.new_bpm
        }

    @staticmethod
    def dict_to_hymn(dictionary):
        """
        Converts a dictionary to a LibraryHymn object.

        Args:
            dictionary (dict): The dictionary representation of the LibraryHymn object.

        Returns:
            LibraryHymn: The created LibraryHymn object.
        """
        markers = [Marker(**marker_dict) for marker_dict in dictionary.get('markers', [])]
        track_channels = dictionary.get('track_channels', {})
        track_channels = {int(k): v for k, v in track_channels.items()}  # Convert keys to integers

        return LibraryHymn(
            title=dictionary['title'],
            hymn_number=dictionary['hymn_number'],
            path=dictionary['path'],
            kind=dictionary['kind'],
            is_hymn=dictionary['is_hymn'],
            markers=markers,
            track_channels=track_channels,  # Use the dictionary with integer keys
            track_names=dictionary.get('track_names', {}),
            time_signature=dictionary.get('time_signature', {}),
            key_signature=dictionary.get('key_signature'),
            bpm=dictionary.get('bpm', 120),
            new_bpm=dictionary.get('new_bpm', dictionary.get('bpm'))
        )

class Marker:
    """
    Represents a marker.

    Attributes:
        title (str): The title of the marker.
        start_time (int): The start time of the marker.
        stop_time (int): The stop time of the marker.
        stops (list): List of stops.
    """

    def __init__(self, title, start_time, stop_time=0, stops=None, is_selected=True):
        self.title = title
        self.start_time = start_time
        self.stop_time = stop_time
        self.stops = [Stop(**stop) if isinstance(stop, dict) else stop for stop in (stops or [])]
        self.is_selected = is_selected

    def get_short_title(self):
        """
        Returns the short title of the marker.

        Returns:
            str: The short title of the marker.
        """
        return "Intro" if "Intro" in self.title else self.title.replace("Verse", "V")

    def to_dict(self):
        """
        Converts the Marker object to a dictionary.

        Returns:
            dict: The dictionary representation of the Marker object.
        """
        return {
            "title": self.title,
            "start_time": self.start_time,
            "stop_time": self.stop_time,
            "stops": [stop.to_dict() if isinstance(stop, Stop) else stop for stop in self.stops],
            'is_selected': self.is_selected
        }

class OrganPlayerModel:
    """
    Represents the model for an organ player application.
    """

    def __init__(self):
        """
        Initializes the OrganPlayerModel class.
        """
        self.playlist = {}
        self.library = {}
        self.midi_device = None

    def get_short_titles(self, markers):
        """
        Returns a list of short titles for the given markers.

        Args:
            markers (list): List of markers.

        Returns:
            list: List of short titles.
        """
        return [Marker.get_short_title(marker) for marker in markers]

    def get_midi_device(self):
        """
        Returns the MIDI device name.

        Returns:
            str: MIDI device name.
        """
        midi_devices = mido.get_output_names()
        for device in midi_devices:
            if "UM-ONE" in device:
                return device
        for device in midi_devices:
            if "loopMIDI" in device:
                return device
        return None

    def get_midi_devices(self):
        """
        Returns a list of available MIDI devices.

        Returns:
            list: List of available MIDI devices.
        """
        return mido.get_output_names()

    def set_midi_device(self, device):
        """
        Sets the MIDI device.

        Args:
            device (str): MIDI device name.
        """
        self.midi_device = device

    def update_library_hymn(self, hymn):
        """
        Updates the library hymn.

        Args:
            hymn (LibraryHymn): The library hymn.
        """
        self.library[f"{hymn.hymn_number}-{hymn.title}"] = hymn
        self.save_cache(os.path.join(BASE_DIR, "cache.json"), self.library)

    def clear_playlist(self):
        """
        Clears the playlist.
        """
        self.playlist = {}

    def remove_from_playlist(self, hymn):
        """
        Removes the hymn from the playlist.

        Args:
            hymn (PlaylistHymn): The playlist hymn.
        """
        self.playlist.pop(f"{hymn.hymn_number}-{hymn.title}-{hymn.abbreviated_titles}")

    def edit_playlist_item(self, hymn, index):
        """
        Edits the playlist item.

        Args:
            hymn (PlaylistHymn): The playlist item.
        """
        self.playlist[f"{hymn.hymn_number}-{hymn.title}-{hymn.abbreviated_titles}"] = hymn

    def load_playlist(self, filename):
        """
        Loads a playlist from the given filename.

        Args:
            filename (str): Path to the playlist file.

        Returns:
            list: Loaded playlist.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            loaded_playlist = json.load(f)
        return self._convert_to_hymn(loaded_playlist)

    def _convert_to_hymn(self, loaded_playlist):
        """
        Converts the loaded playlist to a list of hymns.

        Args:
            loaded_playlist (list): Loaded playlist.

        Returns:
            list: List of hymns.
        """
        playlist = []
        for hymn_dict in loaded_playlist:
            hymn = PlaylistHymn.dict_to_hymn(hymn_dict)
            playlist.append(hymn)
            if hymn.is_hymn:
                self.playlist[f"{hymn.hymn_number}-{hymn.title}-{hymn.abbreviated_titles}"] = hymn
        return playlist

    def save_playlist(self, playlist, filename):
        """
        Saves the playlist to the given filename.

        Args:
            playlist (list): Playlist to be saved.
            filename (str): Path to save the playlist.
        """
        save_list = []
        for i, item in enumerate(playlist):
            hymn = self.get_hymn_from_playlist(item['values'])
            if hymn is not None:
                save_list.append(hymn.to_dict(i))
            else:
                seperator = PlaylistHymn(
                    title=item['values'][1],
                    hymn_number=item['values'][0],
                    path="",
                    kind=item['values'][2],
                    is_hymn=False,
                    abbreviated_titles=item['values'][2]
                ).to_dict(i)
                save_list.append(seperator)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_list, f)

    def update_cache(self, midi_file, kind):
        """
        Updates the cache with the metadata of the MIDI file.

        Args:
            midi_file (str): Path to the MIDI file.
            kind (str): Type of the MIDI file.

        Returns:
            tuple: Tuple containing the MIDI file, metadata, hymn, and kind.
        """
        print(midi_file)
        metadata = self.read_midi_metadata(midi_file)
        metadata['kind'] = kind
        hymn = LibraryHymn.dict_to_hymn(metadata)
        return midi_file, metadata, hymn, kind

    def sysex_to_mido(self, sysex_string):
        """
        Converts the SysEx string to a mido.Message.

        Args:
            sysex_string (str): SysEx string.

        Returns:
            mido.Message: Converted message.
        """
        # Convert the SysEx string to a mido.Message
        message = mido.Message.from_hex(sysex_string)
        # Return the message
        return message

    def open_midi_output(self, midi_device):
        """
        Opens the MIDI output.

        Args:
            midi_device (str): MIDI device name.

        Returns:
            mido.MidiOutput: MIDI output object.
        """
        return mido.open_output(midi_device, autoreset=True)

    def reset_midi_output(self, outport):
        """
        Resets the MIDI output.

        Args:
            outport (mido.MidiOutput): MIDI output object.
        """
        print("Resetting MIDI output")

        for channel in range(11, 15):
            for note in range(0, 128):
                outport.send(mido.Message('note_off', channel=channel, note=note, velocity=0, time=0))

    def close_midi_output(self, outport):
        """
        Closes the MIDI output.

        Args:
            outport (mido.MidiOutput): MIDI output object.
        """
        outport.close()

    def stops_to_sysex(self, engaged_stops):
        """
        Converts the engaged stops to a SysEx string.

        Args:
            engaged_stops (list): List of engaged stops.

        Returns:
            str: SysEx string.
        """
        # Convert the engaged stops to a SysEx string
        return get_sysex(engaged_stops if len(engaged_stops) > 0 else [])

    def send_midi_message(self, msg, outport=None):
        """
        Sends a MIDI message once.

        Args:
            msg (mido.Message): MIDI message.
            outport (mido.MidiOutput, optional): MIDI output object. Defaults to None.
        """
        if outport is None:
            midi_device = self.get_midi_device()
            # Open the MIDI port
            if midi_device != None:
                outport = mido.open_output(midi_device)
                # Send the message
                outport.send(msg)
                # Close the MIDI port
                outport.close()
        else:
            outport.send(msg)

    def refresh_library_thread(self, reloadCache, total_files_callback, update_progress_callback):
        """
        Refreshes the library in a separate thread.

        Args:
            reloadCache (bool): Flag indicating whether to reload the cache.
            total_files_callback (function): Callback function for total files.
            update_progress_callback (function): Callback function for progress update.

        Returns:
            dict: Refreshed library.
        """
        start_time = time.time()
        midi_path = ""
        cache = {}
        if (not reloadCache and os.path.exists(os.path.join(BASE_DIR, "cache.json"))):
            temp_cache = self.load_cache(os.path.join(BASE_DIR, "cache.json"))
            for key, hymn in temp_cache.items():
                kind = hymn['kind']
                if kind not in cache:
                    cache[kind] = {}
                cache[kind][key] = hymn

        files_to_process = []

        for kind, midi_path in kind_to_folder.items():
            if kind not in cache:
                cache[kind] = {}
            if not os.path.exists(midi_path):
                continue
            midi_files = []
            for entry in os.scandir(midi_path):
                if entry.is_file() and entry.name.endswith('.mid'):
                    relative_path = os.path.relpath(os.path.join(midi_path, entry.name), BASE_DIR)
                    midi_files.append((relative_path, kind))
            midi_files = [(midi_file, kind) for midi_file, kind in midi_files if not any(midi_file == hymn['path'] for hymn in cache[kind].values())]
            files_to_process.extend(midi_files)

        if len(files_to_process) > 0:
            if total_files_callback is not None:
                total_files_callback(len(files_to_process))
            max_workers = multiprocessing.cpu_count() - 1  # Leave one core free for the main thread

            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.update_cache, midi_file, kind) for midi_file, kind in files_to_process]
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    path, proto_hymn, hymn, kind = future.result()
                    cache[kind][path] = proto_hymn
                    if update_progress_callback is not None:
                        update_progress_callback(i + 1)
        for kind_hymns in cache.values():
            for hymn in kind_hymns.values():
                hymn = LibraryHymn.dict_to_hymn(hymn)
                print(hymn.path)
                self.library[f"{hymn.hymn_number}-{hymn.title}"] = hymn
        self.save_cache(os.path.join(BASE_DIR, "cache.json"), self.library)
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"The function took {execution_time} seconds to run.")
        return self.library
    
    def add_hymn_to_library(self, hymn):
        """
        Adds the hymn to the library.

        Args:
            hymn (LibraryHymn): The library hymn.
        """

        designated_folder = kind_to_folder.get(hymn.kind, kind_to_folder["Other"])
        
        self.update_hymn_name(hymn)

        new_path = shutil.move(hymn.path, designated_folder)
        new_name = f"{hymn.hymn_number} {hymn.title}{os.path.splitext(new_path)[1]}"
        final_path = os.path.join(designated_folder, new_name)
        os.rename(new_path, final_path)
        
        # Update the path of the hymn
        hymn.path = os.path.relpath(final_path, BASE_DIR)
        
        self.library[f"{hymn.hymn_number}-{hymn.title}"] = hymn
        self.save_cache(os.path.join(BASE_DIR, "cache.json"), self.library)

    def update_hymn_name(self, hymn):
        midi = mido.MidiFile(hymn.path)
        for msg in midi.tracks[0]:
            if msg.type == 'track_name':
                msg.name = f"{hymn.hymn_number} {hymn.title}"
                return
        msg = mido.MetaMessage('track_name', name=f"{hymn.hymn_number} {hymn.title}", time=0)
        midi.tracks[0].insert(0, msg)
        midi.save(hymn.path)

    def scan_for_markers(self, midi_file):
        """
        Scans the MIDI file for markers.

        Args:
            midi_file (str): Path to the MIDI file.

        Returns:
            tuple: Tuple containing the title, number, key signature, time signature, BPM, markers, and channel instrument.
        """
        markers_and_times = []
        title = ""
        number = ""
        key_signature = ""
        time_signature = {}
        accumulated_time = 0.0
        end_time = 0.0

        with mido.MidiFile(midi_file) as midi:
            bpm = 120
            tempo = 500000
            for msg in midi.tracks[0]:
                if msg.time > 0:
                    delta = mido.tick2second(msg.time, midi.ticks_per_beat, tempo)
                else:
                    delta = 0
                accumulated_time += delta
                if msg.type == 'track_name':
                    parts = msg.name.split(" ", 1)
                    number = parts[0]
                    title = parts[1] if len(parts) > 1 else ""
                elif msg.type == 'key_signature':
                    key_signature = msg.key
                elif msg.type == 'time_signature':
                    time_signature['numerator'] = msg.numerator
                    time_signature['denominator'] = msg.denominator
                elif msg.type == 'marker':
                    msg_text = msg.text
                    if any(word in msg_text for word in ["Amen", "Verse", "Intro", "End"]):
                        if "Intro" in msg_text:
                            markers_and_times.append(Marker(msg_text, accumulated_time))
                        else:
                            markers_and_times[-1].stop_time = accumulated_time
                            markers_and_times.append(Marker(msg_text, accumulated_time))
                elif msg.type == 'end_of_track':
                    if len(markers_and_times) > 0:
                        markers_and_times[-1].stop_time = accumulated_time
                    end_time = accumulated_time
                elif msg.type == 'set_tempo':
                    tempo = msg.tempo
            bpm = mido.tempo2bpm(tempo, (time_signature['numerator'], time_signature['denominator']))

            if len(markers_and_times) == 0:
                markers_and_times.append(Marker("Entire", 0, end_time))

            # # initialize all known tracks with notes
            channel_instrument = {}
            channel = 0
            for track in midi.tracks:
                for msg in track:
                    if msg.type == "note_on":
                        channel_instrument[channel] = f"Track {channel}"
                        break
                channel += 1

            # # Check for Program Changes
            # channel = 0
            # for msg in mido.merge_tracks(midi.tracks):
            #     if msg.type == "program_change":
            #         channel_instrument[channel] = program_change_dict[msg.program + 1]
            #     elif msg.type == "note_on":
            #         break
            #     channel += 1

        markers_dict_list = [marker.to_dict() for marker in markers_and_times]
        return title, number, key_signature, time_signature, bpm, markers_dict_list, channel_instrument

    def read_midi_metadata(self, file_path):
        """
        Reads the metadata of the MIDI file.

        Args:
            file_path (str): Path to the MIDI file.

        Returns:
            dict: Metadata of the MIDI file.
        """
        title, number, key_signature, time_signature, bpm, markers_and_times, track_names = self.scan_for_markers(file_path)
        return {'title': title, 'hymn_number': number, 'key_signature': key_signature, 'time_signature': time_signature, 'bpm': bpm, 'is_hymn': True, 'markers': markers_and_times, 'path': file_path, 'track_names': track_names}

    def load_cache(self, file_path):
        """
        Loads the cache from the given file.

        Args:
            file_path (str): Path to the cache file.

        Returns:
            dict: Loaded cache.
        """
        if not os.path.exists(file_path):
            return
        if os.name == 'nt' and os.path.exists(file_path):
            ctypes.windll.kernel32.SetFileAttributesW(file_path, 32)  # 32 = FILE_ATTRIBUTE_NORMAL
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_cache(self, file_path, library):
        """
        Saves the cache to the given file.

        Args:
            file_path (str): Path to save the cache.
            library (dict): Library to be saved.
        """
        library_dict = {key: hymn.to_dict() for key, hymn in library.items()}
        if os.name == 'nt' and os.path.exists(file_path):
            ctypes.windll.kernel32.SetFileAttributesW(file_path, 32)  # 32 = FILE_ATTRIBUTE_NORMAL
        with open(file_path, 'w', encoding='utf-8') as f:
            if not os.path.splitext(file_path)[1]:
                file_path += ".json"
            json.dump(library_dict, f)
            # If on Windows, add the hidden attribute
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(file_path, 2)  # 2 = FILE_ATTRIBUTE_HIDDEN

    def get_current_title(self, midi_file):
        """
        Gets the current title from the MIDI file.

        Args:
            midi_file (str): Path to the MIDI file.
        """
        with mido.MidiFile(midi_file) as midi:
            for msg in midi.tracks[0]:
                if msg.type == 'track_name':
                    return msg.name
        return None

    def get_all_markers(self):
        markers = []
        for hymn in self.library:
            markers.extend(hymn.markers)
        return markers

    def get_hymn_from_library(self, item):
        try:
            hymn = self.library[f"{item[0]}-{item[1]}"]
        except KeyError:
            hymn = None
        return hymn

    def get_hymn_from_playlist(self, item):
        return self.playlist.get(f"{item[0]}-{item[1]}-{item[2]}")
    
    def convert_library_hymn_to_playlist_hymn(self, library_hymn):
        return PlaylistHymn.from_library_hymn(library_hymn)

    def add_to_playlist(self, playlist_hymn):
        if playlist_hymn.is_hymn:
            self.playlist[f"{playlist_hymn.hymn_number}-{playlist_hymn.title}-{playlist_hymn.abbreviated_titles}"] = playlist_hymn
            return playlist_hymn
