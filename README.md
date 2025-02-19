# dofus-switcher
Scripts for managing Dofus windows when multiboxing.

This is a simple repository for holding some utility scripts I've been working on for Dofus.

Among them are (currently):
- `x11_switcher.py`, a script for switching between Dofus windows while using the X11 Window System.
- `kde/`, which contains scripts for running on KDE using Wayland.

## KDE Wayland

Dependencies:

**kdotool**: https://aur.archlinux.org/packages/kdotool-git

Packages:
```bash
sudo pacman -S python-evdev python-pydbus python-gobject
```

The Wayland security model makes it so we can't listen to key presses from arbitrary applications. This is generally a really good thing! But it does make it harder to write this sort of window switcher. Thus, there are several parts to make this work:

### `org.saone.dofusswitcher.conf`:

This file has a dbus configuration to allow my user as well as `root` access a DBus System Bus for communication. On my system, it gets copied to `/usr/share/dbus-1/system.d/org.saone.dofusswitcher.conf`, followed by a system reboot. 

### `kdot_switcher.py`

This file provides a DBus Service with an extremely simple interface - it takes strings sent from `evdev_pipe.py`, and uses `kdotool` to give windows focus.

This has to be run _after_ setting up the above config file, should be started _before_ the `evdev_pipe.py` (though it isn't mandatory).

Run via:
```bash
python3 kdot_switcher.py
```

### `evdev_pipe.py`

This file takes a list of keys to listen to and an input device, and connects to the DBus service in `kdot_switcher.py`, and sends key events to that service. In order to avoid this simply being a keylogger, it only sends the six specific keys needed for `kdot_switcher.py` to work.

Because this service is reading from a `/dev/input/` device, it needs root access to run. Feel free to check [the code](kde/evdev_pipe.py) - it's pretty readable to verify you're not just running a keylogger.

Run via:
```bash
sudo python3 evdev_pipe.py
```

## TODO:

I'd like to make these pick up configs from .ini files, or command line options or something. Right now, I'm just focusing on getting things basically working.

I could eventually make this into a package that automatically sets things up based on your system and such, but I'm still building out basic functionality for me to use, so volunteers are welcome to chat with me or submit a PR.

Supposedly Ankama will be building in a window switcher to Dofus Unity eventually, but I need my window switcher in the meantime.
