# Philips RS232 controller
from modules.philips_controller import PhilipsController
import os, sys, platform


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

if __name__ == "__main__":
    philips_controller.check_if_database_exist()
    print(philips_controller.get_screen_version())
    print(philips_controller.get_screen_settings())


