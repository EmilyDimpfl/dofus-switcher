#!/usr/bin/env python3
# This script should be run as root, and will send specific keyboard events to a
#  userspace program via dbus.
from pathlib import Path
import time
import pydbus
from evdev import InputDevice, categorize, ecodes, list_devices

# Keys to pipe:
listen_keys = ["KEY_F4", "KEY_F5", "KEY_F6", "KEY_F7", "KEY_F8", "KEY_PAUSE"]

# dbus stuff:
def setup_dbus() -> pydbus.bus.Bus:
    # Set up our system bus.
    bus = pydbus.SystemBus()

    # Define the service, path, and interface
    service_name = "org.saone.dofusswitcher"

    # Register the object on the bus
    bus_obj = bus.get(service_name)
    
    return bus_obj


def emit_key_event(bus: pydbus.bus.Bus, key_name: str) -> None:
    # Emit a signal on the dbus bus when a key is pressed
    bus.KeyPressed(key_name)

def get_keyboard(input_device: str) -> InputDevice:
    input_device = str(Path(input_device).resolve())
    # List available devices
    devices = list_devices()

    # Find the first keyboard device
    keyboard = None
    for device in devices:
        dev = InputDevice(device)
        if input_device == dev.path:
            keyboard = dev
            print(f"Found keyboard device: {dev.name} ({dev.path})")
            break

    if not keyboard:
        print("No keyboard device found!")
        exit()
    return keyboard

def main():
    # Device to listen to:
    input_device = "/dev/input/by-id/usb-DuckyChannel_International_Co.__Ltd._Ducky_Keyboard-event-kbd"
    # todo: provide this via argparse or env var or something
    keyboard = get_keyboard(input_device)

    # get dbus interface to send on:
    interface = setup_dbus()

    print("Listening for key presses...")
    try:
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:  # Key press (value 1)
                key_event = categorize(event)
                key_name = key_event.keycode
                if key_name in listen_keys: # only listen for specific keys
                    emit_key_event(interface, key_name)
            time.sleep(0.01) # cede CPU
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
