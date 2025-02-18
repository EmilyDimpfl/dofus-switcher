#!/usr/bin/env python

"""
This is a window switcher for the MMORPG Dofus, written on Arch Linux with KDE on Wayland.

It depends on `kdotool`, which you can install via AUR: https://aur.archlinux.org/packages/kdotool-git

It uses kdotool to control windows, and is incompatible with X11 (as far as I'm aware).

It receives key presses from a dbus daemon running privileged to read input via evdev.

"""

import os
import subprocess

from gi.repository import GLib
from pydbus import SystemBus

# map keys to window titles:
# note: these values will be re-populated with the window IDs
key_to_window = {
    "KEY_F5": "Dofus",
    "KEY_F6": "Dofus",
    "KEY_F7": "Dofus",
    "KEY_F8": "Dofus",
}

# window binding:
bind_to_window_key = "KEY_PAUSE"
BINDING = False

# vars for cycling through accounts:
cycle_key = "KEY_F4"
ini_order = list(key_to_window.keys())
LAST_ACC = len(ini_order) - 1
NUM_ACCTS = len(ini_order)


def rebind_active_window(key: str) -> None:
    # 1. find the currently active window ID:
    #    $ kdotool getactivewindow
    #    > {447960db-a391-4219-bb5a-5a0aa2c549b3}
    # 2. verify that that is a Dofus.x64 window:
    #    $ kdotool getwindowclassname {447960db-a391-4219-bb5a-5a0aa2c549b3}
    #    > Dofus.x64
    # 3. set the window ID as the `key`'s value
    active_window_result = subprocess.run(
        ["kdotool", "getactivewindow"], stdout=subprocess.PIPE, text=True
    )
    active_window_id = active_window_result.stdout.strip()

    class_name_result = subprocess.run(
        ["kdotool", "getwindowclassname", active_window_id],
        stdout=subprocess.PIPE,
        text=True,
    )
    class_name = class_name_result.stdout.strip()
    print(f"Got window class {class_name} for ID {active_window_id}")

    if class_name != "Dofus.x64":
        print("Warning: attempted to bind non-Dofus window to key, ignoring.")
        return

    global key_to_window
    key_to_window[key] = active_window_id
    print(f"Set {key.name} to window ID {active_window_id}.")


def activate_window(win_id: str) -> None:
    os.system(f"kdotool windowactivate {win_id}")


def on_press(key):
    global BINDING, LAST_ACC, NUM_ACCTS
    try:
        if key == bind_to_window_key:
            # toggle window renaming mode
            BINDING = not BINDING
            print(f"Binding: {BINDING}")
        elif BINDING and key in key_to_window:
            rebind_active_window(key)
        elif key in key_to_window:
            activate_window(key_to_window[key])
        elif key == cycle_key:
            next_win = ini_order[LAST_ACC % NUM_ACCTS]
            activate_window(next_win)
            LAST_ACC = (LAST_ACC + 1) % NUM_ACCTS
    except Exception as e:
        print(f"Error: {e}")


class DofusSwitcherService(object):
    """
    <node>
        <interface name='net.lew21.pydbus.ClientServerExample'>
            <method name='KeyPressed'>
                <arg type='s' name='a' direction='in'/>
            </method>
            <method name='Quit'/>
        </interface>
    </node>
    """

    def KeyPressed(self, key: str):
        """Does app logic based on the key press"""
        print(f"Got keypress: {key}")
        on_press(key)

    def Quit(self):
        """removes this object from the DBUS connection and exits"""
        loop.quit()


loop = GLib.MainLoop()
bus = SystemBus()
bus.publish("org.saone.dofusswitcher", DofusSwitcherService())
loop.run()
