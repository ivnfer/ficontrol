# Philips RS232 controller
from modules.philips_controller import PhilipsController
import os, sys, platform
import typer
from typing_extensions import Annotated


app = typer.Typer(add_completion=False)
VERSION = "v2.3 2023/07/13"


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
        _version: bool = typer.Option(None, "--version", callback=version_callback)):
    pass


@app.command(help="Obtiene la información del monitor y la muestra por pantalla.")
def status(
        now: Annotated[bool, typer.Option(help="Obtiene la información actual de la pantalla.")] = False,
        last: Annotated[bool, typer.Option(help="Obtiene el último estado registrado de la pantalla")] = False,
        updateinfo: Annotated[bool, typer.Option(help="Registra en base de datos la información de la pantalla")] = False
):
    if now:
        philips_controller.print_screen_info()
        philips_controller.insert_info_db()
    if last:
        philips_controller.print_screen_last_info()
    if updateinfo:
        philips_controller.insert_info_db()


@app.command(help="Enciende o apaga el monitor")
def power(
        on: Annotated[bool, typer.Option(help="Enciende el monitor")] = False,
        off: Annotated[bool, typer.Option(help="Apaga el monitor")] = False
):
    if on:
        philips_controller.set_power_status("on")
    elif off:
        philips_controller.set_power_status("off")


@app.command(help="Cambia el input del monitor")
def input_source(
    hdmi1: Annotated[bool, typer.Option(help="Cambia el input al HDMI 1")] = False,
    hdmi2: Annotated[bool, typer.Option(help="Cambia el input al HDMI 2")] = False,
    hdmi3: Annotated[bool, typer.Option(help="Cambia el input al HDMI 3")] = False
):
    if hdmi1:
        philips_controller.set_input_source("hdmi1")
    elif hdmi2:
        philips_controller.set_input_source("hdmi2")
    elif hdmi3:
        philips_controller.set_input_source("hdmi3")


@app.command(help="Cambia el arranque fte del monitor")
def boot_source(
    hdmi1: Annotated[bool, typer.Option(help="Cambia el arranque fte al HDMI 1")] = False,
    hdmi2: Annotated[bool, typer.Option(help="Cambia el arranque fte al HDMI 2")] = False,
    hdmi3: Annotated[bool, typer.Option(help="Cambia el arranque fte al HDMI 3")] = False

):
    if hdmi1:
        philips_controller.set_boot_source("hdmi1")
    elif hdmi2:
        philips_controller.set_boot_source("hdmi2")
    elif hdmi3:
        philips_controller.set_boot_source("hdmi3")


@app.command(help="Establece el brillo en el monitor")
def brillo(value: int):
    philips_controller.set_brightness(value)


@app.command(help="Establece el contraste en el monitor")
def contraste(value: int):
    philips_controller.set_contrast(value)


@app.command(help="Establece el volumen en el monitor")
def volume(value: int):
    philips_controller.set_volume(value)


@app.command(help="Activa/Desactiva el mute en el monitor")
def mute(
        on: Annotated[bool, typer.Option(help="Activa el mute")] = None,
        off: Annotated[bool, typer.Option(help="Desactiva el mute")] = None
):
    if on:
        philips_controller.set_mute("on")
    elif off:
        philips_controller.set_mute("off")


@app.command(help="Establece el modo de ahorro energético del monitor, valores [1-4]")
def modoahorro(value: int):
    philips_controller.set_power_saving_mode(value)


@app.command(help="Activa/Desactiva el onewire en el monitor")
def onewire(
        on: Annotated[bool, typer.Option(help="Activa el onewire en el monitor")] = None,
        off: Annotated[bool, typer.Option(help="Desactiva el onewire en el monitor")] = None
):
    if on:
        philips_controller.set_onewire("on")
    elif off:
        philips_controller.set_onewire("off")


@app.command(help="Comandos adicionales para configurar el monitor")
def options(
        autosetup: Annotated[bool, typer.Option(help="Aplica la configuración al monitor en función de su modelo")] = None,
        video_default: Annotated[bool, typer.Option(help="Resetea los valores de vídeo al 50 (brillo, contraste, color, tono, etc.)")] = None,
):
    if autosetup:
        philips_controller.auto_screen_setup()
    if video_default:
        philips_controller.set_video_default()


if __name__ == '__main__':
    app()

