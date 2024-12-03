# Philips RS232 Control
RS232 control script for Philips displays

Allows to send commands to philips displays using RS232 protocol. Works on windows and linux.


## How it works

The following actions can be performed:

```text
X:\path\to\script> python phicontrol.py --help

Usage: phicontrol.py [OPTIONS] COMMAND [ARGS]...

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


To check how works a specific command just add <code>--help</code> after the argument, for example:
```text
phicontrol status --help
                                                                                                                                                                                                                                                                                                                    
 Usage: phicontrol status [OPTIONS]                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                    
 Get screen info/status                                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                                    
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --now       --no-now         Gets the current information from the screen. [default: no-now]                                                                                                                                                                                                                     │
│ --last      --no-last        Gets the last recorded status of the screen [default: no-last]                                                                                                                                                                                                                      │
│ --update    --no-update      Updates database with the screen information [default: no-update]                                                                                                                                                                                                                   │
│ --log       --no-log         Shows last 7 days logs [default: no-log]                                                                                                                                                                                                                                            │
│ --help                       Show this message and exit.                                                                                                                                                                                                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### Settings
Serial ports can be changed editing the <code>db/phicontrol.yaml</code> file:

```yaml
# Linux serial port
# If RS232 is connected throught USB port: /dev/ttyUSB0
# If RS232 is connected throught serial port: /dev/ttyS0
linux_serial_port: /dev/ttyUSB0


# Windows serial port
# Select the COM port where RS232 is connected.
windows_serial_port: COM3
```

