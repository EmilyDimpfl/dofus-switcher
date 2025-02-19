#!/usr/bin/env python

"""
This is a window switcher for the MMORPG Dofus, written on Arch Linux with KDE on Wayland.

It depends on `kdotool`, which you can install via AUR: https://aur.archlinux.org/packages/kdotool-git

It uses kdotool to control windows.It receives key presses from a dbus daemon
 running privileged to read input via evdev. `kdotool` is a KDE-exclusive tool, but
 with some effort this could be expanded to work with a variety of backends.

"""

import os
import subprocess

from gi.repository import GLib
from pydbus import SystemBus

# map keys to window titles:
# note: these values will be re-populated with the window IDs
key_to_window = {
    "KEY_F5": None,
    "KEY_F6": None,
    "KEY_F7": None,
    "KEY_F8": None,
}

# window binding:
bind_to_window_key = "KEY_PAUSE"
BINDING = False

# vars for cycling through accounts:
cycle_key = "KEY_F4"
cycle_order = list(key_to_window.keys())
# note: `cycle_order` can be initialized in a different order, like:
# cycle_order = list("KEY_F7", "KEY_F5", "KEY_F8", "KEY_F6")
# ...in order to define a custom initiative order.
LAST_ACC = len(cycle_order) - 1
NUM_ACCTS = len(cycle_order)


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

    global key_to_window, cycle_order
    # update the key-to-id map:
    key_to_window[key] = active_window_id
    print(f"Set {key} to window ID {active_window_id}.")


def activate_window(win_id: str) -> None:
    print(f"Activating window {win_id}")
    os.system(f"kdotool windowactivate {win_id}")


def cycle_next_acct() -> None:
    global LAST_ACC, NUM_ACCTS
    print(cycle_order)

    next_win = None
    next_win_key = None

    # prevent infinite loops:
    if not any(list(key_to_window.values())):
        print("Aborting cycle, no Dofus windows set.")
        return

    while next_win is None:
        next_win_key = cycle_order[LAST_ACC % NUM_ACCTS]
        next_win = key_to_window[next_win_key]
        LAST_ACC = (LAST_ACC + 1) % NUM_ACCTS
        print(f"while status: LAST_ACC: {LAST_ACC}, next_win: {next_win}, next_win_key: {next_win_key}")
    if next_win is None:
        print(f"Unable to cycle; LAST_ACC: {LAST_ACC}, next_win: {next_win}, next_win_key: {next_win_key}")
        return
    print(f"cycling window, LAST_ACC: {LAST_ACC}, next_win: {next_win}, next_win_key: {next_win_key}")
    activate_window(next_win)


def on_press(key):
    global BINDING
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
            cycle_next_acct()
    except Exception as e:
        print(f"Error: {e}")


class DofusSwitcherService(object):
    """
    <node>
        <interface name='org.saone.dofusswitcher'>
            <method name='KeyPressed'>
                <arg type='s' name='a' direction='in'/>
            </method>
        </interface>
    </node>
    """

    def KeyPressed(self, key: str):
        """Does app logic based on the key press"""
        print(f"Got keypress: {key}")
        on_press(key)


loop = GLib.MainLoop()


def main():
    try:
        bus = SystemBus()
        bus.publish("org.saone.dofusswitcher", DofusSwitcherService())
        loop.run()
    except KeyboardInterrupt:
        print("\nGoodbye")


if __name__ == "__main__":
    main()
