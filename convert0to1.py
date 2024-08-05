import mido
from mido import MidiFile, MidiTrack

def convert_type_0_to_type_1(input_file, output_file):
    # Load the existing MIDI Type 0 file
    mid = MidiFile(input_file)

    # Ensure the file is Type 0
    if mid.type != 0:
        raise ValueError("The input file is not a Type 0 MIDI file")

    # Create a new MIDI Type 1 file
    new_mid = MidiFile(type=1)

    # Create a track 0 for SysEx and marker events
    composer_track = MidiTrack()
    new_mid.tracks.append(composer_track)

    # Create a dictionary to hold tracks for each channel
    channel_tracks = {}
    last_time = {}

    # Initialize last_time for each track
    last_time['meta'] = 0
    for i in range(16):
        last_time[i] = 0

    # Distribute events into separate tracks based on channels
    absolute_time = 0
    for msg in mid.tracks[0]:
        absolute_time += msg.time
        if msg.type == 'meta' or msg.type == 'sysex':
            # Add SysEx and marker events to the composer track
            delta_time = absolute_time - last_time['meta']
            last_time['meta'] = absolute_time
            composer_track.append(msg.copy(time=delta_time))
        elif msg.type in ['note_on', 'note_off', 'control_change', 'program_change']:
            # Add channel messages to their respective tracks
            if msg.channel not in channel_tracks:
                channel_tracks[msg.channel] = MidiTrack()
                new_mid.tracks.append(channel_tracks[msg.channel])
            delta_time = absolute_time - last_time[msg.channel]
            last_time[msg.channel] = absolute_time
            channel_tracks[msg.channel].append(msg.copy(time=delta_time))

    # Save the new MIDI Type 1 file
    new_mid.ticks_per_beat = mid.ticks_per_beat
    new_mid.filename = mid.filename
    new_mid.save(output_file)



# Example usage
input_file = 'test_type0.mid'
output_file = 'test_type1.mid'

convert_type_0_to_type_1(input_file, output_file)