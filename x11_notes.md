We need to figure out which window is which which, because it seems like on non-Windows systems the window title is just "Dofus".

We can use wmctrl to list and identify windows, and rename their titles. Renaming the title is convenient for identifying the windows, and can also be useful for picking the window with `wmctrl -a`.

Get windows with PIDs `wmctrl -l -p`
Set window title: `wmctrl -i -r 0x06600005 -N "NewName"`
Raise window: `wmctrl -a WindowName`


We can figure out which process is running a Dofus instance:
```
emily@Wittgenbuntu:~/.local/share/applications$ ps aux | grep Dofus
emily      19586  190  4.5 11892840 3014828 ?    Sl   22:31  33:28 ./Dofus.x64 --logfile /home/emily/.config/zaap/gamesLogs/dofus-dofus3/dofus.log --port 26116 --gameName dofus --gameRelease dofus3 --instanceId 1 --hash 46520c75-67b6-4fde-8bb8-084800130eb2 --canLogin true -logFile /home/emily/.config/zaap/gamesLogs/dofus-dofus3/dofus.log --langCode en --autoConnectType 1 --connectionPort 5555 --configUrl https://dofus2.cdn.ankama.com/config/release_linux.json
```

Most of this is generic and doesn't change from instance to instance, but there's an `--instanceId 1` in there, which we can use.

We can also get the PID of each window with `wmctrl -l -p`:

```
emily@Wittgenbuntu:~$ wmctrl -l -p
0x00c00003  0 5128   Wittgenbuntu Ankama Launcher
0x01e00005 -1 5285   Wittgenbuntu #general😺 | Zarya Fan Club 😻 - Discord
0x05400015  0 10956  Wittgenbuntu switcher.py - ankaswitcher - Visual Studio Code
...
0x02600005  0 67004  Wittgenbuntu Dofus
```

```
emily@Wittgenbuntu:~$ ps ax -o pid,comm,args | grep Dofus
  67004 Dofus.x64       ./Dofus.x64 --logfile /home/emily/.config/zaap/gamesLogs/dofus-dofus3/dofus.log --port 26116 --gameName dofus --gameRelease dofus3 --instanceId 7 --hash e3827f5e-1546-45d7-b304-9c95bed24e65 --canLogin true -logFile /home/emily/.config/zaap/gamesLogs/dofus-dofus3/dofus.log --langCode en --autoConnectType 1 --connectionPort 5555 --configUrl https://dofus2.cdn.ankama.com/config/release_linux.json
```

```python
accounts = {
    "Branwen1": ["Saone", "Suuna", "Azeban", "Suna", "Saorahn", "Saona", "Camma"],
    "Branwen2": ["Artinia", "Durga", "Hienen", "Satwo", "Neytrea", "Sabea"],
    "Branwen3": ["Senrine", "Saomea", "Niekkata", "Liapa", "Saluan"],
    "Branwen4": ["Souuna", "Nanagri", "Heplia", "Insaranda", "Nynphar"],
}
```


https://superuser.com/questions/382616/detecting-currently-active-window