#!/usr/bin/env python3

"""
This is a window switcher for the MMORPG Dofus, on Ubuntu Linux 24.04.

You can install xdotool, xprop, and wmctrl with `apt install xdotool wmctrl x11-utils -y`

It uses wmctrl and xdotool to control the windows, and is incompatible with Wayland.

It requires the user to name the window before it will work, using the [pause] key to start 
 renaming mode, and then pressing F5-F8 while the corresponding window is active.

Once the window is renamed, toggle the renaming back off, and use F5-F8 to activate game windows.
"""

import os
import subprocess
import re
from pynput import keyboard


# map keys to window titles:
key_to_window = {
    keyboard.Key.f5: "Dofus 1",
    keyboard.Key.f6: "Dofus 2",
    keyboard.Key.f7: "Dofus 3",
    keyboard.Key.f8: "Dofus 4",
}

# window renaming:
bind_to_window_key = keyboard.Key.pause
BINDING = False

# vars for cycling through accounts:
cycle_key = keyboard.Key.f4
ini_order = ["Dofus 1", "Dofus 2", "Dofus 3", "Dofus 4"]
LAST_ACC = 3
NUM_ACCTS = 4


def rename_active_window(name: str) -> None:
    # get active window via `xprop -id $(xdotool getwindowfocus) | grep WM_CLASS | grep "Dofus.x64"`
    # window id:
    xdotool_result = subprocess.run(['xdotool', 'getwindowfocus'], stdout=subprocess.PIPE, text=True)
    window_id = xdotool_result.stdout.strip()
    # WM_CLASS:
    xprop_result = subprocess.run(['xprop', '-id', window_id], stdout=subprocess.PIPE, text=True)
    window_props: list[str] = xprop_result.stdout.split("\n")

    # ref: https://unix.stackexchange.com/a/494170
    # Find the WM_CLASS field, which currently looks like:
    # WM_CLASS(STRING) = "Dofus.x64", "Dofus.x64"
    # These are two strings:
    # - A string that names the particular instance of the application. 
    # - A string that names the general class of application.
    # We'll care about the second string. Maybe the first string will be more descriptive in the future, 
    #  and we can just use that to identify windows and skip this whole business.

    wm_class = None
    for line in window_props:
        if line.startswith('WM_CLASS(STRING) = "'):
            # get tokens between double quotes:
            matches: list[str] = re.findall(r'"([^"]+)"', line)
            # get the last match:
            wm_class = matches[-1]

    if wm_class is None or wm_class != 'Dofus.x64':
        # we have the wrong window type, ignore this input
        return
    
    # wm_class is 'Dofus.x64', we can rename the window:    
    os.system(f'wmctrl -i -r {window_id} -N "{name}"')


def activate_window(name: str) -> None:
    os.system(f'wmctrl -a "{name}"')


def on_press(key):
    global BINDING, LAST_ACC, NUM_ACCTS
    try:
        if key == bind_to_window_key:
            # toggle window renaming mode
            BINDING = not BINDING
            print(f"Binding: {BINDING}")
        elif BINDING and key in key_to_window:
            rename_active_window(key_to_window[key])
        elif key in key_to_window:
            activate_window(key_to_window[key])
        elif key == cycle_key:
            next_win = ini_order[LAST_ACC % NUM_ACCTS]
            activate_window(next_win)
            LAST_ACC = (LAST_ACC + 1) % NUM_ACCTS
    except Exception as e:
        print(f"Error: {e}")


def main():
    # Start the key listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
