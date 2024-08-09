import mido

def main():
    # List available MIDI input ports
    print("Available MIDI input ports:")
    for port in mido.get_input_names():
        print(port)

    # Open the first available MIDI input port
    input_port_name = mido.get_input_names()[0]
    with mido.open_input(input_port_name) as inport:
        print(f"Listening for MIDI messages on {input_port_name}...")

        # Poll for MIDI messages
        while True:
            for msg in inport.iter_pending():
                print(msg)

if __name__ == "__main__":
    main()