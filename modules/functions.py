import sys
import os
import platform
import yaml


def get_absolute_path():
    if getattr(sys, 'frozen', False):
        return os.path.realpath(os.path.dirname(sys.executable))
    else:
        return os.path.realpath(os.path.dirname("phicontrol.py"))


def check_system_serial_port(config_file):
    with open(config_file) as file:
        config = yaml.safe_load(file)
        sys_platform = platform.system().lower()

        linux_port = config["rs232"]["linux_serial_port"]
        windows_port = config["rs232"]["windows_serial_port"]

        if sys_platform == "windows":
            return windows_port
        else:
            return linux_port


def read_yaml_config_file(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)