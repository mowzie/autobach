import time
import mido
import mido.backends.rtmidi
from mido import MetaMessage, MidiTrack
from mido.midifiles import tick2second

class MidiFile(mido.MidiFile):
    def __init__(self, **kwargs):
        self.bpm_scaler = 1.0
        self.starting_message_number = 0
        self.starting_timestamp = 0
        self.ending_timestamp = 0
        super().__init__(**kwargs)

    def set_bpm_scaler(self, bpm_scaler):
        self.bpm_scaler = bpm_scaler

    def play(self, meta_messages=True, starting_timestamp=0, ending_timestamp=0):
        """Play back all tracks.

        The generator will sleep between each message by
        default. Messages are yielded with correct timing. The time
        attribute is set to the number of seconds slept since the
        previous message.

        You will receive copies of the original messages, so you can
        safely modify them without ruining the tracks.
        """
        sleep = time.sleep
        self.starting_timestamp = starting_timestamp
        self.ending_timestamp = ending_timestamp
        accumulated_time = 0.0
        played_first_message = False
        start_time = time.time()
        for (msg, _) in self:
            accumulated_time += msg.time / self.bpm_scaler
            playback_time = time.time() - start_time
            duration_to_next_event = accumulated_time - playback_time

            if played_first_message:
                if duration_to_next_event > 0:
                    sleep(duration_to_next_event)
            if not played_first_message and msg.type == 'note_on' and msg.velocity > 0:
                played_first_message = True

            if isinstance(msg, MetaMessage) and not meta_messages:
                continue
            else:
                yield (msg, accumulated_time)

    def __iter__(self):
        # The tracks of type 2 files are not in sync, so they can
        # not be played back like this.
        if self.type == 2:
            raise TypeError("can't merge tracks in type 2 (asynchronous) file")

        tempo = 500000

        # Merge the tracks
        merged_tracks = _merge_tracks(self.tracks)
        accumulated_time = 0.0

        for i, (msg, track_name) in enumerate(merged_tracks):
            delta = tick2second(msg.time, self.ticks_per_beat, tempo) if msg.time > 0 else 0
            accumulated_time += delta
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.type in {'sysex', 'control_change'}:
                yield (msg.copy(time=delta), track_name)
            if msg.type == "note_on" and accumulated_time >= self.starting_timestamp:
                starting_message_number = i
                break

        break_flag = False
        for (msg, track_name) in merged_tracks[starting_message_number:]:
            if msg.time > 0:
                delta = tick2second(msg.time, self.ticks_per_beat, tempo)
            else:
                delta = 0
            accumulated_time += delta
            if accumulated_time >= self.ending_timestamp:
                break_flag = True

            yield (msg.copy(time=delta), track_name)
            if msg.type == 'marker' and break_flag:
                break
            if msg.type == 'set_tempo':
                tempo = msg.tempo

def _merge_tracks(tracks):
    """Returns a MidiTrack object with all messages from all tracks.

    The messages are returned in playback order with delta times
    as if they were all in one track.
    """
    messages = []
    for track in tracks:
        messages.extend(_to_abstime(track, track.name))

    messages.sort(key=lambda msg: msg[0].time)
    return MidiTrack(fix_end_of_track(_to_reltime(messages)))

def _to_reltime(messages):
    """Convert messages to relative time."""
    now = 0
    for (msg, track_name) in messages:
        delta = msg.time - now
        yield (msg.copy(time=delta), track_name)
        now = msg.time

def _to_abstime(messages, track_name):
    """Convert messages to absolute time."""
    now = 0
    for msg in messages:
        now += msg.time
        new_msg = msg.copy(time=now)
        yield new_msg, track_name

def fix_end_of_track(messages):
    """Remove all end_of_track messages and add one at the end.

    This is used by merge_tracks() and MidiFile.save()."""
    # Accumulated delta time from removed end of track messages.
    # This is added to the next message.
    accum = 0

    for (msg, track_name) in messages:
        if msg.type == 'end_of_track':
            accum += msg.time
        else:
            if accum:
                delta = accum + msg.time
                yield (msg.copy(time=delta), track_name)
                accum = 0
            else:
                yield (msg, track_name)
    yield MetaMessage('end_of_track', time=accum), None
