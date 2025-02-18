
Searches for open Dofus windows:
```bash
$ kdotool search --class "Dofus.x64"
{232e1e18-7af5-472b-9687-04624608aa3c}
```
Only raises the window, doesn't give it focus:
`$ kdotool windowraise {232e1e18-7af5-472b-9687-04624608aa3c}`

Raises + focuses the window:
`$ kdotool windowactivate {232e1e18-7af5-472b-9687-04624608aa3c}`

kdotool search --class "Dofus.x64" --name "Dofus"
