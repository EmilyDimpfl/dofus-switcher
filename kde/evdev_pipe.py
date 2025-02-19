#!/usr/bin/env python3
# This script should be run as root, and will send specific keyboard events to a
#  userspace program via dbus.
from pathlib import Path
from time import sleep
from pydbus.bus import Bus
from pydbus import SystemBus
from evdev import InputDevice, categorize, ecodes, list_devices

from gi.repository.GLib import GError

# Keys to pipe:
listen_keys = ["KEY_F4", "KEY_F5", "KEY_F6", "KEY_F7", "KEY_F8", "KEY_PAUSE"]
# Device to listen to:
input_device = "/dev/input/by-id/usb-DuckyChannel_International_Co.__Ltd._Ducky_Keyboard-event-kbd"


# dbus stuff:
def setup_dbus() -> Bus:
    # Set up our system bus.
    bus = SystemBus()

    # Define the service, path, and interface
    service_name = "org.saone.dofusswitcher"

    # Register the object on the bus
    bus_obj = bus.get(service_name)

    return bus_obj

def retry_setup_dbus() -> Bus:
    # get dbus interface to send on:
    while True:
        try:
            interface = setup_dbus()
            return interface
        except GError:
            # error connecting to the dbus
            print("Error: unable to connect to bus.")
        sleep(5)


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
        exit(1)
    return keyboard


def relay_keypresses(kb: InputDevice, bus: Bus):
    print("Listening for key presses...")
    for event in kb.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:  # Key press (value 1)
            key_event = categorize(event)
            key_name = key_event.keycode
            # only listen for specific keys:
            if key_name in listen_keys:
                # Emit a signal on the dbus bus when a key is pressed
                bus.KeyPressed(key_name)
        sleep(0.01)  # cede CPU


def main():
    try:
        # todo: provide this via argparse or env var or something
        keyboard = get_keyboard(input_device)

        # get dbus interface to send on:
        interface = retry_setup_dbus()

        relay_keypresses(keyboard, interface)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
