import sys
import socket
import serial
import sqlite3
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.status import Status



class PhilipsController:
    def __init__(self, serial_port, database_path):
        self.serial_port = serial_port
        self.control = 0x01
        self.group = 0x00

        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(f"{self.database_path}/control.db")
        self.cursor = self.connection.cursor()

    def check_if_database_exist(self):
        if os.path.exists(self.database_path):
            pass
        else:
            os.mkdir(self.database_path)


    def send_command(self, _timeout, message_size, ip=None, port=5000,  **kwargs):
        try:

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

            command += chr(checksum)  # Añade al comando el checksum calculado
            if ip is not None:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.settimeout(5)
                soc.connect((ip, port))
                soc.send(command.encode('latin1'))
                response = soc.recv(1024)
                soc.close()
                return response

            else:
                ser = serial.Serial(self.serial_port)
                ser.baudrate = 9600
                ser.bytesize = 8
                ser.timeout = 5

                ser.write(bytes(command, "latin1"))
                response = ser.read(_timeout)
                ser.close()
                return response.hex()

        except ValueError:
            print("Value Error")
            return b"0".hex()

        except serial.SerialException as e:
            print(f"Serial Error: {e}")
            sys.exit(1)

        except Exception as err:
            print(err)
            sys.exit(1)

    def get_screen_version(self):
        model = self.send_command(15, 0x06, data0=0xA1, data1=0x00)
        serialnumber = self.send_command(19, 0x05, data0=0x15)
        firmware = self.send_command(12, 0x06, data0=0xA1, data1=0x01)
        build_date = self.send_command(15, 0x06, data0=0xA1, data1=0x02)
        sicp_version = self.send_command(10, 0x06, data0=0xA2, data1=0x00)
        platform_label = self.send_command(13, 0x06, data0=0xA2, data1=0x01)
        platform_version = self.send_command(8, 0x06, data0=0xA2, data1=0x02)

        try:
            get_model = bytes.fromhex(model[8:-2]).decode('utf-8')
            get_serialnumber = bytes.fromhex(serialnumber[8:-2]).decode('utf-8')
            get_firmware = bytes.fromhex(firmware[8:-2]).decode('utf-8')
            get_build_date = bytes.fromhex(build_date[8:-2]).decode('utf-8')
            get_sicp_version = bytes.fromhex(sicp_version[8:-2]).decode('utf-8')
            get_platform_label = bytes.fromhex(platform_label[8:-2]).decode('utf-8')
            get_platform_version = bytes.fromhex(platform_version[8:-2]).decode('utf-8')

            return {"model": get_model, "serialnumber": get_serialnumber, "firmware": get_firmware,
                    "build_date": get_build_date, "sicp_version": get_sicp_version, "platform_label": get_platform_label,
                    "platform_version": get_platform_version}

        except Exception as error:
            print(error)

    def get_screen_settings(self):
        try:
            power_state = self.send_command(6, 0x05, data0=0x19)
            boot_source = self.send_command(7, 0x05, data0=0xba)  # Necesaria versión SICP v2.05
            input_source = self.send_command(9, 0x05, data0=0xAD)
            volume = self.send_command(6, 0x05, data0=0x45)
            mute = self.send_command(6, 0x05, data0=0x46)
            power_saving_mode = self.send_command(6, 0x05, data0=0xD3)
            onewire = self.send_command(6, 0x05, data0=0xbc)  # Necesaria versión SICP v2.07

            get_power_state = self.get_hex_value(power_state[8:10], 6)
            get_boot_source = self.get_hex_value(boot_source[8:10], 1)
            get_input_source = self.get_hex_value(input_source[8:10], 1)

            try:
                get_volume = int(volume[8:10], 16)
            except ValueError:
                get_volume = "Cant`t read data"

            get_mute = self.get_hex_value(mute[8:10], 5)
            get_power_saving_mode = self.get_hex_value(power_saving_mode[8:10], 2)
            get_onewire = self.get_hex_value(onewire[8:10], 3)

            return {"power_state": get_power_state, "boot_source": get_boot_source, "input_source": get_input_source,
                    "volume": get_volume, "mute": get_mute, "power_saving_mode": get_power_saving_mode,
                    "onewire": get_onewire}

        except Exception as error:
            print(error)

    def get_screen_video(self):
        try:
            video_settings = self.send_command(12, 0x0C, data0=0x33, data1=0x37, data2=0x37, data3=0x37, data4=0x37,
                                               data5=0x37, data6=0x37, data7=0x03)

            get_brightness = int(video_settings[8:10], 16)
            get_colour = int(video_settings[10:12], 16)
            get_contrast = int(video_settings[12:14], 16)
            get_sharpness = int(video_settings[14:16], 16)
            get_tone = int(video_settings[16:18], 16)
            get_black_level = int(video_settings[18:20], 16)
            get_gamma = int(video_settings[20:22], 16)

            return {"brightness": get_brightness, "colour": get_colour, "contrast": get_contrast,
                   "sharpness": get_sharpness, "tone": get_tone, "black_level": get_black_level, "gamma": get_gamma}

        except ValueError:
            err = "Cant`t read data"
            return {"brightness": err, "colour": err, "contrast": err,
                    "sharpness": err, "tone": err, "black_level": err, "gamma": err}

    def print_screen_last_info(self):
        self.cursor.execute("SELECT * FROM history_status ORDER BY updated DESC LIMIT 1")
        rows = self.cursor.fetchall()
        table = Table(title="Última actualización", style="bright_white")
        table.add_column("[grey89]Parameter", no_wrap=True, style="grey89")
        table.add_column("[bright_white]Value", no_wrap=True, style="bright_white")

        for row in rows:
            table.add_row("Model", row[1])
            table.add_row("Serial Number", row[2])
            table.add_row("Firmware", row[3])
            table.add_row("Build Date", row[4])
            table.add_row("Platform Label", row[5])
            table.add_row("Platform Version", row[6])
            table.add_row("SICP Version", row[7], end_section=True)
            table.add_row("Power State", row[8])
            table.add_row("Boot Source", row[9])
            table.add_row("Input Source", row[10])
            table.add_row("Volume", row[11])
            table.add_row("Mute", row[12])
            table.add_row("Power Saving Mode", row[13])
            table.add_row("One Wire", row[14], end_section=True)
            table.add_row("Brightness", row[15])
            table.add_row("Contrast", row[16])
            table.add_row("Colour", row[17])
            table.add_row("Sharpness", row[18])
            table.add_row("Tone", row[19])
            table.add_row("Black Level", row[20])
            table.add_row("Gamma", row[21], end_section=True)
            table.add_row("Last Update", row[22], style="yellow")

        Console().print(table, justify="left")

    def print_screen_info(self):

        loading_spinner = Status("Getting screen data...")

        loading_spinner.start()
        screen_version = self.get_screen_version()
        video_settings = self.get_screen_settings()
        screen_video = self.get_screen_video()
        loading_spinner.stop()

        table = Table(title="Sreen Info", style="bright_white")
        table.add_column("[grey89]Parameter", no_wrap=True, style="grey89")
        table.add_column("[bright_white]Value", no_wrap=True, style="bright_white")

        table.add_row('Model', screen_version['model'])
        table.add_row('Serial Number', screen_version['serialnumber'])
        table.add_row('Firmware', screen_version['firmware'])
        table.add_row('Build Date', screen_version['build_date'])
        table.add_row('Platform Label', screen_version['platform_label'])
        table.add_row('Platform Version', screen_version['platform_version'])
        table.add_row('SICP Version', screen_version['sicp_version'], end_section=True)
        table.add_row("Power State", video_settings['power_state'])
        table.add_row('Boot Source', video_settings['boot_source'])
        table.add_row('Input Source', video_settings['input_source'])
        table.add_row('Volume', str(video_settings['volume']))
        table.add_row('Mute', video_settings['mute'])
        table.add_row('Power Saving Mode', video_settings['power_saving_mode'])
        table.add_row('Onewire', video_settings['onewire'], end_section=True)
        table.add_row('Brightness', str(screen_video['brightness']))
        table.add_row('Contrast', str(screen_video['contrast']))
        table.add_row('Colour', str(screen_video['colour']))
        table.add_row('Sharpness', str(screen_video['sharpness']))
        table.add_row('Tone', str(screen_video['tone']))
        table.add_row('Black level', str(screen_video['black_level']))
        table.add_row('Gamma', str(screen_video['colour']))

        Console().print(table, justify="left")

    def add_to_history_table(self):
        loading_spinner = Status("Saving data...")
        loading_spinner.start()
        version = self.get_screen_version()
        settings = self.get_screen_settings()
        video = self.get_screen_video()

        self.cursor.execute("SELECT DATETIME('now', 'localtime')")
        localtime = self.cursor.fetchone()[0]

        insert_query = f"""INSERT INTO history_status (modelname, serialnumber, fwversion, build_date, platform_label,
                 platform_version, sicp_version, powerstatus, bootsource, input, volume, mute, powermode, onewire,
                  brightness, color, contrast, sharpness, tint, black_level, gamma, updated) VALUES 
                  ('{version['model']}','{version['serialnumber']}', '{version['firmware']}', '{version['build_date']}',
                  '{version['platform_label']}', '{version['platform_version']}', '{version['sicp_version']}',
                  '{settings['power_state']}', '{settings['boot_source']}', '{settings['input_source']}',
                  '{settings['volume']}', '{settings['mute']}','{settings['power_saving_mode']}',  '{settings['onewire']}',
                  '{video['brightness']}', '{video['colour']}', '{video['contrast']}', '{video['sharpness']}',
                  '{video['tone']}', '{video['black_level']}', '{video['gamma']}', '{localtime}')"""

        self.cursor.execute(insert_query)
        self.connection.commit()
        loading_spinner.stop()

    def delete_old_records(self):
        self.cursor.execute("SELECT DATETIME('now', 'localtime', '-7 day')")
        limit_date = self.cursor.fetchone()[0]

        delete_query = f"""DELETE from history_status WHERE updated <='{limit_date}'"""
        self.cursor.execute(delete_query)
        self.connection.commit()

    def clean_history_records(self):
        # noinspection SqlWithoutWhere
        delete_rows = "DELETE FROM history_status"
        self.cursor.execute(delete_rows)

        delete_rowid = """DELETE FROM sqlite_sequence where name='history_status'"""
        self.cursor.execute(delete_rowid)

        self.connection.commit()

    def print_screen_history(self):

        select_query = f"""SELECT modelname, serialnumber, powerstatus, bootsource, input, volume, mute, powermode,
        onewire, brightness, contrast, updated FROM history_status"""

        self.cursor.execute(select_query)
        rows = self.cursor.fetchall()

        table = Table(title="Last 7 days log", style="bright_white")
        table.add_column(header="Date", style="yellow", justify="center", no_wrap=True)
        table.add_column(header="Power", justify="center")
        table.add_column(header="Boot Source", justify="center")
        table.add_column(header="Input Source", justify="center")
        table.add_column(header="Volume", justify="center")
        table.add_column(header="Mute", justify="center")
        table.add_column(header="Power Mode", justify="center")
        table.add_column(header="One Wire", justify="center")
        table.add_column(header="Brightness", justify="center")
        table.add_column(header="Constrast", justify="center")
        for row in rows:

            table.add_row(row[11], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                          row[10])

        Console().print(table, justify="left")

        self.delete_old_records()

    def get_hex_value(self, hexcode, groupid: int):
        try:
            _query = f"SELECT codename from hexcodes where hexcode='{hexcode}' and idtype={groupid}"
            self.cursor.execute(_query)
            return self.cursor.fetchone()[0]
        except TypeError:
            return "Hexcode not found"

    def set_power_status(self, power_status: str):
        if power_status.lower() == "on":
            print("Sending command...")
            self.send_command(6, 0x06, data0=0x18, data1=0x02)
        elif power_status.lower() == "off":
            print("Sending command...")
            self.send_command(6, 0x06, data0=0x18, data1=0x01)

    def set_volume(self, volume: int):
        print(f"Setting volume: {volume}")
        self.send_command(6, 0x07, data0=0x44, data1=volume, data2=volume)

    def set_power_saving_mode(self, power_saving_mode: int):
        print(f"Setting power saving mode {power_saving_mode}")
        if power_saving_mode == 1:
            self.send_command(6, 0x06, data0=0xD2, data1=0x04)
        elif power_saving_mode == 2:
            self.send_command(6, 0x06, data0=0xD2, data1=0x05)
        elif power_saving_mode == 3:
            self.send_command(6, 0x06, data0=0xD2, data1=0x06)
        elif power_saving_mode == 4:
            self.send_command(6, 0x06, data0=0xD2, data1=0x07)
        else:
            print(f"Power saving mode {power_saving_mode} not exists")

    def set_onewire(self, onewire: str):
        print(f"Setting onewire: {onewire}")
        if onewire.lower() == "on":
            self.send_command(6, 0x06, data0=0xBD, data1=0x01)
        elif onewire.lower() == "off":
            self.send_command(6, 0x06, data0=0xBD, data1=0x00)

    def set_input_source(self, input_source: str):
        print(f"Setting input source {input_source}")
        if input_source.lower() == "hdmi1":
            self.send_command(6, 0x09, data0=0xAC, data1=0x0d, data2=0x01, data3=0x01, data4=0x00)
        elif input_source.lower() == "hdmi2":
            self.send_command(6, 0x09, data0=0xAC, data1=0x06, data2=0x01, data3=0x01, data4=0x00)
        elif input_source.lower() == "hdmi3":
            self.send_command(6, 0x09, data0=0xAC, data1=0x0f, data2=0x01, data3=0x01, data4=0x00)

    def set_boot_source(self, boot_source: str):
        print(f"Setting boot source: {boot_source}")
        if boot_source.lower() == "hdmi1":
            self.send_command(6, 0x07, data0=0xbb, data1=0x0d, data2=0x00)
        elif boot_source.lower() == "hdmi2":
            self.send_command(6, 0x07, data0=0xbb, data1=0x06, data2=0x00)
        elif boot_source.lower() == "hdmi3":
            self.send_command(6, 0x07, data0=0xbb, data1=0x0f, data2=0x00)

    def set_mute(self, mute: str):
        if mute == "on":
            print("Sending command...")
            self.send_command(6, 0x06, data0=0x47, data1=0x01)
        elif mute == "off":
            print("Sending command...")
            self.send_command(6, 0x06, data0=0x47, data1=0x00)

    def set_brightness(self, brightness: int):
        loading_spinner = Status(f"Setting brightness: {brightness}")
        loading_spinner.start()
        video_settings = self.get_screen_video()
        try:
            self.send_command(6, 0x0c, data0=0x32, data1=brightness, data2=video_settings['colour'],
                              data3=video_settings['contrast'], data4=video_settings['sharpness'],
                              data5=video_settings['tone'], data6=video_settings['black_level'],
                              data7=video_settings['gamma'])
            print("Applied settings")
            loading_spinner.stop()

        except Exception as err:
            print(f"Error: {err}")

    def set_contrast(self, contrast: int):
        loading_spinner = Status(f"Setting contrast: {contrast}")
        loading_spinner.start()
        video_settings = self.get_screen_video()
        try:
            self.send_command(6, 0x0c, data0=0x32, data1=video_settings['brightness'],
                              data2=video_settings['colour'], data3=contrast, data4=video_settings['sharpness'],
                              data5=video_settings['tone'], data6=video_settings['black_level'],
                              data7=video_settings['gamma'])
            print("Applied settings")

            loading_spinner.stop()

        except Exception as err:
            print(f"Error: {err}")

    def set_video_default(self):
        loading_spinner = Status(f"Settings default video settings...")
        loading_spinner.start()

        try:
            self.send_command(6, 0x0c, data0=0x32, data1=50, data2=50, data3=50, data4=50, data5=50, data6=50, data7=1)
            print("Settings applied")

            loading_spinner.stop()
        except Exception as error:
            print(f"Error: {error}")

    def auto_screen_setup(self):
        loading_spinner = Status(f"Setting up monitor")
        loading_spinner.start()

        screen_version = self.get_screen_version()

        platform_label = screen_version['platform_label']

        current_input_source = self.send_command(9, 0x05, data0=0xAD)

        database_power_saving_mode = 0
        database_onewire = 0

        self.cursor.execute(f"""SELECT * from screenconfig WHERE platform='{platform_label}'""")
        rows = self.cursor.fetchall()
        if rows:
            for row in rows:
                database_power_saving_mode = int(row[3], 16)
                database_onewire = int(row[4], 16)

            self.send_command(6, 0x07, data0=0xbb, data1=int(current_input_source[8:10], 16), data2=0x00)
            self.send_command(6, 0x06, data0=0xD2, data1=database_power_saving_mode)
            self.send_command(6, 0x06, data0=0xBD, data1=database_onewire)
            print("Applied settings")

        else:
            print(f"Monitor settings not found: {platform_label}")

        loading_spinner.stop()
