# ficontrol
Philips RS232 remote control

Allows to send commands to philips displays via RS232. Works on windows (COM3) and linux (/dev/ttyUSB0).

The following operations can be performed:

```
X:\path\to\script> python ficontrol.py --help

Usage: ficontrol.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --version          Displays script version                                                          │
│ --help             Show this message and exit.                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────╮
│ bootsource           Change the source boot of the screen                                           │
│ brightness           Sets the screen brightness                                                     │
│ contrast             Sets the screen contrast                                                       │
│ inputsource          Change screen input source                                                     │
│ mute                 Enable/Disable mute                                                            │
│ onewire              Enable/Disable HDMI One Wire                                                   │
│ options              Additional commands to configure the screen                                    │
│ power                Turns the screen on or off                                                     │
│ powermode            Sets the screen power saving mode, values [1-4]                                │
│ status               Obtains information from the screen                                            │
│ volume               Sets the screen volume                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
