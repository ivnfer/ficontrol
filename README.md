# Philips RS232 Control
RS232/TCP control cli tool for Philips SICP displays.

Allows to send commands to philips displays using RS232 protocol. Works on windows and linux.


## How it works

The following actions can be performed:

```text
❯ phicontrol --help
                                                                                                                                                 
 Usage: phicontrol [OPTIONS] COMMAND [ARGS]...                                                                                                   
                                                                                                                                                 
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --ip             IP_ADDRESS  IP address or hostname                                                                                           │
│                              [default: None]                                                                                                  │
│ --version                    Displays script version                                                                                          │
│ --help                       Show this message and exit.                                                                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ bootsource   Change the boot source                                                                                                           │
│ brightness   Change screen brightness                                                                                                         │
│ contrast     Change screen contrast                                                                                                           │
│ inputsource  Change screen input source                                                                                                       │
│ mute         Enable/Disable mute                                                                                                              │
│ onewire      Enable/Disable HDMI One Wire                                                                                                     │
│ options      Additional commands to configure the screen                                                                                      │
│ power        Turns the screen on/off                                                                                                          │
│ powermode    Change screen power saving mode, values [1-4]                                                                                    │
│ status       Get screen info/status                                                                                                           │
│ volume       Change screen volume                                                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
If no IP is given it will try to connect to the screen using RS232 trought the serial port. For example:

```text
❯ phicontrol status --now
              Sreen Info                                                                                                                         
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓                                                                                                           
┃ Parameter         ┃ Value          ┃                                                                                                           
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩                                                                                                           
│ Model             │ 32BDL3550Q     │                                                                                                           
│ Serial Number     │ AU0AXXXXXXXXXX │                                                                                                           
│ Firmware          │ FB02.07        │                                                                                                           
│ Build Date        │ 11/29/2022     │                                                                                                           
│ Platform Label    │ BDL3550Q       │                                                                                                           
│ Platform Version  │ 3.0            │                                                                                                           
│ SICP Version      │ v2.07          │                                                                                                           
├───────────────────┼────────────────┤                                                                                                           
│ Power State       │ OFF            │                                                                                                           
│ Boot Source       │ HDMI 2         │                                                                                                           
│ Input Source      │ HDMI 2         │                                                                                                           
│ Volume            │ 5              │                                                                                                           
│ Mute              │ OFF            │                                                                                                           
│ Power Saving Mode │ 3              │                                                                                                           
│ Onewire           │ OFF            │                                                                                                           
├───────────────────┼────────────────┤                                                                                                           
│ Brightness        │ 80             │                                                                                                           
│ Contrast          │ 50             │                                                                                                           
│ Colour            │ 55             │                                                                                                           
│ Sharpness         │ 10             │                                                                                                           
│ Tone              │ 50             │                                                                                                           
│ Black level       │ 50             │                                                                                                           
│ Gamma             │ 55             │                                                                                                           
└───────────────────┴────────────────┘    
```

To send commands throught ip the option <code>--ip</code> must be used. For example:
```text
❯ phicontrol --ip 192.168.18.146 status --now
              Sreen Info                                                                                                                         
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓                                                                                                           
┃ Parameter         ┃ Value          ┃                                                                                                           
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩                                                                                                           
│ Model             │ 32BDL3550Q     │                                                                                                           
│ Serial Number     │ AU0AXXXXXXXXXX │                                                                                                           
│ Firmware          │ FB02.07        │                                                                                                           
│ Build Date        │ 11/29/2022     │                                                                                                           
│ Platform Label    │ BDL3550Q       │                                                                                                           
│ Platform Version  │ 3.0            │                                                                                                           
│ SICP Version      │ v2.07          │                                                                                                           
├───────────────────┼────────────────┤                                                                                                           
│ Power State       │ OFF            │                                                                                                           
│ Boot Source       │ HDMI 2         │                                                                                                           
│ Input Source      │ HDMI 2         │                                                                                                           
│ Volume            │ 5              │                                                                                                           
│ Mute              │ OFF            │                                                                                                           
│ Power Saving Mode │ 3              │                                                                                                           
│ Onewire           │ OFF            │                                                                                                           
├───────────────────┼────────────────┤                                                                                                           
│ Brightness        │ 80             │                                                                                                           
│ Contrast          │ 50             │                                                                                                           
│ Colour            │ 55             │                                                                                                           
│ Sharpness         │ 10             │                                                                                                           
│ Tone              │ 50             │                                                                                                           
│ Black level       │ 50             │                                                                                                           
│ Gamma             │ 55             │                                                                                                           
└───────────────────┴────────────────┘           

```

To check how to use a specific command just add <code>--help</code> after the argument, for example:
```text
❯ phicontrol status --help
                                                                                                                                                                                                                                                                                                                    
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

```text
❯ phicontrol power --help
                                                                                                                                                 
 Usage: phicontrol power [OPTIONS]                                                                                                               
                                                                                                                                                 
 Turns the screen on/off                                                                                                                         
                                                                                                                                                 
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --on      --no-on       Turn on screen                                                                                                        │
│                         [default: no-on]                                                                                                      │
│ --off     --no-off      Turn off screen                                                                                                       │
│                         [default: no-off]                                                                                                     │
│ --help                  Show this message and exit.                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Settings
Some options can be changed editing the <code>db/config.yaml</code> file:

```yaml
rs232:
  # Linux serial port
  # If RS232 is connected throught USB port: /dev/ttyUSB0
  # If RS232 is connected throught serial port: /dev/ttyS0
  linux_serial_port: /dev/ttyUSB0

  # Windows serial port
  # Select the COM port where RS232 is connected.
  windows_serial_port: COM3

tcp:
  # TCP port, default 5000
  port: 5000
  # Timeout for tcp connection
  timeout: 5
```

