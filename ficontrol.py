# Philips RS232 controller
# SICP Version 2.07
from modules.philips_controller import PhilipsController
import os, sys, platform
import typer
from typing_extensions import Annotated


app = typer.Typer(add_completion=False)
VERSION = "v2.3.1 2023/07/26"


def get_absolute_path():
    if getattr(sys, 'frozen', False):
        return os.path.realpath(os.path.dirname(sys.executable))
    else:
        return os.path.realpath(os.path.dirname(__file__))


def check_system_serial_port():
    if platform.system().lower() == "windows":
        return "COM3"
    else:
        return "/dev/ttyUSB0"


philips_controller = PhilipsController(serial_port=check_system_serial_port(),
                                       database_path=f"{get_absolute_path()}/db")

philips_controller.check_if_database_exist()


def version_callback(value: bool):
    if value:
        print(f"ficontrol {VERSION}")
        raise typer.Exit()


@app.callback()
def common(
        ctx: typer.Context,
        _version: bool = typer.Option(None, "--version", callback=version_callback, help="Displays script version")):
    pass


@app.command(help="Obtains information from the screen")
def status(
        now: Annotated[bool, typer.Option(help="Gets the current information from the screen.")] = False,
        last: Annotated[bool, typer.Option(help="Gets the last recorded status of the screen")] = False,
        update: Annotated[bool, typer.Option(help="Updates database with the screen information")] = False
):
    if now:
        philips_controller.print_screen_info()
        philips_controller.insert_info_db()
    if last:
        philips_controller.print_screen_last_info()
    if update:
        philips_controller.insert_info_db()


@app.command(help="Turns the screen on or off")
def power(
        on: Annotated[bool, typer.Option(help="Turn on screen")] = False,
        off: Annotated[bool, typer.Option(help="Turn off screen")] = False
):
    if on:
        philips_controller.set_power_status("on")
    elif off:
        philips_controller.set_power_status("off")


@app.command(help="Change screen input source")
def inputsource(
    hdmi1: Annotated[bool, typer.Option(help="Change the input source to HDMI 1")] = False,
    hdmi2: Annotated[bool, typer.Option(help="Change the input source to HDMI 2")] = False,
    hdmi3: Annotated[bool, typer.Option(help="Change the input source to HDMI 3")] = False
):
    if hdmi1:
        philips_controller.set_input_source("hdmi1")
    elif hdmi2:
        philips_controller.set_input_source("hdmi2")
    elif hdmi3:
        philips_controller.set_input_source("hdmi3")


@app.command(help="Change the source boot of the screen")
def bootsource(
    hdmi1: Annotated[bool, typer.Option(help="Change the source boot to HDMI 1")] = False,
    hdmi2: Annotated[bool, typer.Option(help="Change the source boot to HDMI 2")] = False,
    hdmi3: Annotated[bool, typer.Option(help="Change the source boot to HDMI 3")] = False

):
    if hdmi1:
        philips_controller.set_boot_source("hdmi1")
    elif hdmi2:
        philips_controller.set_boot_source("hdmi2")
    elif hdmi3:
        philips_controller.set_boot_source("hdmi3")


@app.command(help="Sets the screen brightness")
def brightness(value: int):
    philips_controller.set_brightness(value)


@app.command(help="Sets the screen contrast")
def contrast(value: int):
    philips_controller.set_contrast(value)


@app.command(help="Sets the screen volume")
def volume(value: int):
    philips_controller.set_volume(value)


@app.command(help="Enable/Disable mute")
def mute(
        on: Annotated[bool, typer.Option(help="Enable mute")] = None,
        off: Annotated[bool, typer.Option(help="Disable mute")] = None
):
    if on:
        philips_controller.set_mute("on")
    elif off:
        philips_controller.set_mute("off")


@app.command(help="Sets the screen power saving mode, values [1-4]")
def powermode(value: int):
    philips_controller.set_power_saving_mode(value)


@app.command(help="Enable/Disable HDMI One Wire")
def onewire(
        on: Annotated[bool, typer.Option(help="Enable HDMI One Wire")] = None,
        off: Annotated[bool, typer.Option(help="Disable HDMI One Wire")] = None
):
    if on:
        philips_controller.set_onewire("on")
    elif off:
        philips_controller.set_onewire("off")


@app.command(help="Additional commands to configure the screen")
def options(
        autosetup: Annotated[bool, typer.Option(help="Applies the configuration to the display according to its model")] = None,
        video_default: Annotated[bool, typer.Option(help="Resets the video values to 50")] = None,
):
    if autosetup:
        philips_controller.auto_screen_setup()
    if video_default:
        philips_controller.set_video_default()


if __name__ == '__main__':
    app()

