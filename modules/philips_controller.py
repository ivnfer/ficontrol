import platform
import sys
import serial
import sqlite3
import os
from pathlib import Path


class SqliteController:
    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(f"{self.database_path}/ficontrol.db")
        self.cursor = self.connection.cursor()

    def custom_select_query(self, query):
        self.cursor.execute(query)
        return self.print_select_query()

    def print_select_query(self):
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)


class PhilipsController:
    def __init__(self, serial_port, database_path):
        self.serial_port = serial_port
        self.control = 0x01
        self.group = 0x00

        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(f"{self.database_path}/ficontrol.db")
        self.cursor = self.connection.cursor()

    def check_if_database_exist(self):
        if os.path.exists(self.database_path):
            pass
        else:
            os.mkdir(self.database_path)

    def send_command(self, timeout, message_size, **kwargs):
        try:
            ser = serial.Serial(self.serial_port)
            ser.baudrate = 9600
            ser.bytesize = 8
            ser.timeout = 5

            data_dictionary = {}
            command = chr(message_size) + chr(self.control) + chr(self.group)
            checksum = message_size ^ self.control ^ self.group

            for data in kwargs:
                data_dictionary.update({f"{data}": kwargs[data]})

            for values in data_dictionary:  # Añade los valores introducidos en el kwargs al checksum
                value = data_dictionary[values]
                checksum ^= value

            for value in data_dictionary:  # Suma los valores añadidos en el kwargs al comando que se va a enviar
                command += chr(data_dictionary[value])

            command += chr(checksum)  # Añade al comando el checsum calculado

            ser.write(bytes(command, "latin1"))
            response = ser.read(timeout)
            ser.close()
            return response.hex()

        except Exception as err:
            print(err)

    def get_screen_version(self):
        model = self.send_command(15, 0x06, data0=0xA1, data1=0x00)
        serialcode = self.send_command(19, 0x05, data0=0x15)
        firmware = self.send_command(12, 0x06, data0=0xA1, data1=0x01)
        build_date = self.send_command(15, 0x06, data0=0xA1, data1=0x02)
        sicp_version = self.send_command(10, 0x06, data0=0xA2, data1=0x00)
        platform_label = self.send_command(13, 0x06, data0=0xA2, data1=0x01)
        platform_version = self.send_command(8, 0x06, data0=0xA2, data1=0x02)
        try:
            get_model = bytes.fromhex(model[8:-2]).decode('utf-8')
            get_serialcode = bytes.fromhex(serialcode[8:-2]).decode('utf-8')
            get_firmware = bytes.fromhex(firmware[8:-2]).decode('utf-8')
            get_build_date = bytes.fromhex(build_date[8:-2]).decode('utf-8')
            get_sicp_version = bytes.fromhex(sicp_version[8:-2]).decode('utf-8')
            get_platform_label = bytes.fromhex(platform_label[8:-2]).decode('utf-8')
            get_platform_version = bytes.fromhex(platform_version[8:-2]).decode('utf-8')

            return {"model": get_model, "serialcode": get_serialcode, "firmware": get_firmware,
                    "build_date": get_build_date, "sicp_version": get_sicp_version, "platform_label": get_platform_label,
                    "platform_version": get_platform_version}

        except Exception as error:
            print(error)

    def get_screen_settings(self):
        power_state = self.send_command(6, 0x05, data0=0x19)
        boot_source = self.send_command(7, 0x05, data0=0xba)
        input_source = self.send_command(9, 0x05, data0=0xAD)
        volume = self.send_command(6, 0x05, data0=0x45)
        mute = self.send_command(6, 0x05, data0=0x46)
        power_saving_mode = self.send_command(6, 0x05, data0=0xD3)
        onewire = self.send_command(6, 0x05, data0=0xbc)
        video_settings = self.send_command(12, 0x0C, data0=0x33, data1=0x37, data2=0x37, data3=0x37, data4=0x37,
                                           data5=0x37, data6=0x37, data7=0x03)
        try:
            get_power_state = self.get_hex_value(power_state[8:10], 6)
            get_boot_source = self.get_hex_value(boot_source[8:10], 1)
            get_input_source = self.get_hex_value(input_source[8:10], 1)
            get_volume = int(volume[8:10], 16)
            get_mute = self.get_hex_value(mute[8:10], 5)
            get_power_saving_mode = self.get_hex_value(power_saving_mode[8:10], 2)
            get_onewire = self.get_hex_value(onewire[8:10], 3)

            get_brightness = int(video_settings[8:10], 16)
            get_colour = int(video_settings[10:12], 16)
            get_contrast = int(video_settings[12:14], 16)
            get_sharpness = int(video_settings[14:16], 16)
            get_tone = int(video_settings[16:18], 16)
            get_black_level = int(video_settings[18:20], 16)
            get_gamma = int(video_settings[20:22], 16)

            return {"powerstate": get_power_state, "boot_source": get_boot_source, "input_source": get_input_source,
                    "volume": get_volume, "mute": get_mute, "power_saving_mode": get_power_saving_mode,
                    "onewire": get_onewire, "brightness": get_brightness, "colour": get_colour,
                    "contrast": get_contrast, "sharpness": get_sharpness, "tone": get_tone,
                    "black_level": get_black_level, "gamma": get_gamma}

        except Exception as error:
            print(error)

    def print_screen_info(self):
        return self.get_screen_version()

    def get_hex_value(self, hexcode, groupid: int):
        try:
            _query = f"SELECT codename from codigos where hexcode='{hexcode}' and idtype={groupid}"
            self.cursor.execute(_query)
            return self.cursor.fetchone()[0]
        except TypeError:
            return "Entrada no registrada en BBDD"

