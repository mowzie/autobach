import os
import argparse
from enum import Enum
from mido import MidiFile, MidiTrack, MetaMessage, Message

def parse_filename(filename):
    # Remove the extension
    name, _ = os.path.splitext(filename)
    
    # Split the name into parts
    parts = name.split()
    
    # Extract the setting number and the rest of the title
    setting_number = parts[1]
    title = ' '.join(parts[2:])
    
    # Transform the setting number
    ds_number = f"DS{setting_number.split('.')[0]}"
    remaining_numbers = '.'.join(setting_number.split('.')[1:])
    # Combine the transformed setting number with the rest of the title
    new_name = f"{ds_number} {remaining_numbers} {title}" if remaining_numbers else f"{ds_number} {title}"
    
    return new_name

class Channels(Enum):
    Great = 11
    Swell = 12
    Pedal = 13
    Choir = 14

def convert_type_0_to_type_1(input_file, output_file, parsed_filename):
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
    new_mid.ticks_per_beat = mid.ticks_per_beat

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
        if isinstance(msg, MetaMessage) or msg.type == 'sysex':
            # Add SysEx and marker events to the composer track
            if msg.type == 'track_name':
                msg.name = parsed_filename
            delta_time = absolute_time - last_time['meta']
            last_time['meta'] = absolute_time
            composer_track.append(msg.copy(time=delta_time))
            if msg.type == 'track_name':
                newMsg = MetaMessage('text', text="Performer: Jeb McGlinchy", time=0)
                composer_track.append(newMsg)
        elif msg.type in ['note_on', 'note_off', 'control_change', 'program_change']:
            # Add channel messages to their respective tracks
            if msg.channel not in channel_tracks:
                channel_tracks[msg.channel] = MidiTrack()
                new_mid.tracks.append(channel_tracks[msg.channel])
                track_name_message = MetaMessage('track_name', name=f"{Channels(msg.channel).name}", time=0)
                channel_tracks[msg.channel].append(track_name_message)
                setOrganMessage = Message('program_change', channel=msg.channel, program=19, time=0)
                channel_tracks[msg.channel].append(setOrganMessage)
            delta_time = absolute_time - last_time[msg.channel]
            last_time[msg.channel] = absolute_time
            channel_tracks[msg.channel].append(msg.copy(time=delta_time))

    # Save the new MIDI Type 1 file
    new_mid.filename = mid.filename
    new_mid.save(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for note overlaps in a MIDI file.")
    parser.add_argument("input_file", type=str, help="Path to the MIDI file")
    args = parser.parse_args()

    filename_with_extension = os.path.basename(args.input_file)
    parsed_filename = parse_filename(filename_with_extension)

    output_file = f"C:\\code\\autobach\\output\\{parsed_filename}.mid"

    convert_type_0_to_type_1(args.input_file, output_file, parsed_filename)