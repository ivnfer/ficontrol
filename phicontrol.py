# Philips RS232 controller
# SICP Version v2.07
from pygments.lexer import default

from modules.philips_controller import PhilipsController
from modules import functions as f
import typer
from typing_extensions import Annotated
import os

app = typer.Typer(add_completion=False, rich_markup_mode="markdown")
VERSION = "v2.6.0 20241203"

db_folder = os.path.join(f.get_absolute_path(), "db")
yaml_file = os.path.join(f.get_absolute_path(), "db/phicontrol.yaml")


philips_controller = PhilipsController(config=yaml_file, database_path=db_folder)
philips_controller.check_if_database_exist()

def ip_callback(ip: str):
    if ip is not None:
        philips_controller.ip = ip


def version_callback(value: bool):
    if value:
        print(f"Philips RS232 Control {VERSION}")
        raise typer.Exit()

@app.callback()
def common(
        ctx: typer.Context,
        ip: str = typer.Option(None, callback=ip_callback, help="**IP** address or **hostname**", metavar="IP_ADDRESS"),
        _version: bool = typer.Option(None, "--version", callback=version_callback, help="Displays script version")
):
    pass


@app.command(help="Get screen info/status")
def status(
        now: Annotated[bool, typer.Option(help="Gets the current information from the screen")] = False,
        last: Annotated[bool, typer.Option(help="Gets the last recorded status of the screen")] = False,
        update: Annotated[bool, typer.Option(help="Updates database with the screen information")] = False,
        log: Annotated[bool, typer.Option(help="Shows last 7 days logs")] = False
):
    if now:
        philips_controller.print_screen_info()
        philips_controller.add_to_history_table()
    if last:
        philips_controller.print_screen_last_info()
    if update:
        philips_controller.add_to_history_table()
    if log:
        philips_controller.print_screen_history()


@app.command(help="Turns the screen on/off")
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


@app.command(help="Change the boot source")
def bootsource(
    hdmi1: Annotated[bool, typer.Option(help="Change the boot source to HDMI 1")] = False,
    hdmi2: Annotated[bool, typer.Option(help="Change the boot source to HDMI 2")] = False,
    hdmi3: Annotated[bool, typer.Option(help="Change the boot source to HDMI 3")] = False

):
    if hdmi1:
        philips_controller.set_boot_source("hdmi1")
    elif hdmi2:
        philips_controller.set_boot_source("hdmi2")
    elif hdmi3:
        philips_controller.set_boot_source("hdmi3")


@app.command(help="Change screen brightness")
def brightness(value: int):
    philips_controller.set_brightness(value)


@app.command(help="Change screen contrast")
def contrast(value: int):
    philips_controller.set_contrast(value)


@app.command(help="Change screen volume")
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


@app.command(help="Change screen power saving mode, values [1-4]")
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
        clean: Annotated[bool, typer.Option(help="Clean all the records stored in database")] = None,
):
    if autosetup:
        philips_controller.auto_screen_setup()
    if video_default:
        philips_controller.set_video_default()
    if clean:
        philips_controller.clean_history_records()


if __name__ == '__main__':
    app()

