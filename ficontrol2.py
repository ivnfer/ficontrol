# Control por puerto serie philips
# Modelos verificados: 43BDL4550D, 32BDL3550Q
# Modelos parcialmente compatibles: BDL3230QL (volumen)
import os
import serial
import argparse
import platform
from tabulate import tabulate
import sqlite3
import sys

# Obtiene la ruta absoluta:
ruta_absoluta = ""
if getattr(sys, 'frozen', False):
    ruta_absoluta = os.path.realpath(os.path.dirname(sys.executable))
else:
    ruta_absoluta = os.path.realpath(os.path.dirname(__file__))


class PhilipsControl:
    def __init__(self):
        # Versión
        self.sw_version = "v2.2 2023/07/13"
        # Si es windows usa el puerto COM
        if platform.system().lower() == 'windows':
            self.puerto_serie = "COM3"
        else:
            self.puerto_serie = "/dev/ttyUSB0"

        # SQLite
        self.dbpath = ruta_absoluta + "/db/"
        self.con = sqlite3.connect(f"{self.dbpath}ficontrol.db")
        self.cur = self.con.cursor()
        self.db_modelo = ""
        self.db_platform = ""
        self.db_powersavingmode = ""
        self.db_onewire = ""
        self.separador = 42*"="

        # Se añaden las variables control y grupo al contructor
        self.control = 0x01
        self.group = 0x00

    @staticmethod
    def str2hex(string_):
        base16 = int(string_, 16)
        hex_value = hex(base16)
        return hex_value

    def enviacomando(self, timeout, msg_size, **kwargs):
        try:
            ser = serial.Serial(self.puerto_serie)
            ser.baudrate = 9600
            ser.bytesize = 8
            ser.timeout = 5

            # Se define una lista en la que se almacenarán los valores de "data" asignados en los parámteros de la función
            dir_valores = {}
            comando = chr(msg_size) + chr(self.control) + chr(self.group)
            checksum = msg_size ^ self.control ^ self.group

            # Realiza las operaciones del checksum y del comando con las variables ya definidas

            # Añade los datos a la lista
            for data in kwargs:
                dir_valores.update({f"{data}": kwargs[data]})
                # print(dir_valores)

            # Extrae datos de la lista
            for valores in dir_valores:
                com = dir_valores[valores]
                checksum ^= com

            for v in dir_valores:
                comando += chr(dir_valores[v])

            # Añade a la variable comando la parte del checksum calculada anteriormente
            # print("Checksum: ", hex(checksum))
            comando += chr(checksum)

            # print("Datos enviados: " + comando.encode("latin1").hex())
            ser.write(bytes(comando, "latin1"))
            res = ser.read(timeout)
            # print(f"Datos recibidos: {res.hex()}")
            # print(100*"=")
            ser.close()
            return res.hex()

        except Exception as error:
            print(f"Se ha producido un error: {error}")
            sys.exit(1)

    def dbcreate(self):
        if os.path.exists(self.dbpath):
            pass
        else:
            os.mkdir(self.dbpath)
        # self.cur.execute("PRAGMA foreign_keys = ON")

    def select_query(self, query):
        # Ejecuta la query introducida por el usuario en la base de datos
        self.cur.execute(query)
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def getcodevalue(self, codedata, groupid: int):
        try:
            _query = f"SELECT codename from codigos where hexcode='{codedata}' and idtype={groupid}"
            self.cur.execute(_query)
            return self.cur.fetchone()[0]
        except TypeError:
            return "Entrada no registrada en BBDD"

    def getscreeninfo(self):
        # Registra en la bbdd información sobre el monitor (modelo, s/n, firmware, build date)
        print("Obteniendo datos del monitor...")
        version = self.get_screen_version(print_status=0)
        screen = self.get_screen_options(print_status=0)
        video = self.get_video_options(print_status=0)

        self.cur.execute("SELECT DATETIME('now', 'localtime')")
        localtime_date = self.cur.fetchone()[0]

        print("Registrando datos en la bbdd...")
        replace_query = f"""REPLACE INTO screeninfo(modelname, serialnumber, fwversion, build_date, platform_label,
                 platform_version, sicp_version, powerstatus, bootsource, input, volume, mute, powermode, onewire,
                  brightness, color, contrast, sharpness, tint, black_level, gamma, updated) VALUES 
                  ('{version['model']}','{version['serialnumber']}', '{version['firmware']}', '{version['build_date']}',
                  '{version['platform_label']}', '{version['platform_version']}', '{version['sicp_version']}',
                  '{screen['power']}', '{screen['bootsource']}', '{screen['input']}', '{screen['volume']}',
                  '{screen['mute']}','{screen['powermode']}',  '{screen['onewire']}', '{video['brillo']}',
                  '{video['color']}', '{video['contraste']}', '{video['definicion']}', '{video['tono']}',
                  '{video['nivel_negro']}', '{video['gamma']}', '{localtime_date}'
                  )"""

        self.cur.execute(replace_query)
        self.con.commit()

    def last_info(self):
        self.cur.execute("SELECT * FROM screeninfo")
        rows = self.cur.fetchall()
        last_info_table = ""
        for row in rows:
            last_info_table = tabulate([
                ["Modelo", row[0]],
                ["Serial Number", row[1]],
                ["Firmware", row[2]],
                ["Build Date", row[3]],
                ["Platform", row[4]],
                ["Platform Version", row[5]],
                ["SICP Version", row[6]],
                ["Power", row[7]],
                ["Arranque Fte.", row[8]],
                ["Input", row[9]],
                ["Volumen", row[10]],
                ["Mute", row[11]],
                ["Modo Ahorro", row[12]],
                ["One Wire", row[13]],
                ["Brillo", row[14]],
                ["Color", row[15]],
                ["Contraste", row[16]],
                ["Definición", row[17]],
                ["Tono", row[18]],
                ["Nivel de negro", row[19]],
                ["Gamma", row[20]],
                ["Fecha registro", row[21]]

            ],
                headers=["Parámetro", "Valor"], tablefmt='orgtbl')

        print(self.separador)
        print("INFORMACIÓN MONITOR")
        print(self.separador)
        print(last_info_table)
        print(self.separador)

    def autoscreensetup(self):
        # Configura la pantalla en función de su modelo, aplica las configuraciones que tiene almacenadas en BBDD.
        print("Configurando monitor...")
        # Obtiene el modelo del monitor
        ask_modelo = self.enviacomando(15, 0x06, data0=0xA1, data1=0x00)
        modelo_monitor = bytes.fromhex(ask_modelo[8:-2]).decode('utf-8')

        ask_platform = self.enviacomando(13, 0x06, data0=0xA2, data1=0x01)
        platform_label = bytes.fromhex(ask_platform[8:-2]).decode('utf-8')
        # Obtiene el input que tiene configurado actualmente
        current_input = self.enviacomando(9, 0x05, data0=0xAD)

        # Selecciona la configuración en función del modelo del monitor
        self.cur.execute(f"""SELECT * from screenconfig WHERE platform= '{platform_label}'""")
        rows = self.cur.fetchall()
        for row in rows:
            self.db_modelo = row[1]
            self.db_platform = row[2]
            self.db_powersavingmode = int(row[3], 16)
            self.db_onewire = int(row[4], 16)

       # print(self.db_modelo, self.db_platform, self.db_powersavingmode, self.db_onewire)
        # Aplica la configuración según el modelo
        # Arranque Fte. Configura la entrada de vídeo actual como arranque fte
        self.enviacomando(6, 0x07, data0=0xbb, data1=int(current_input[8:10], 16), data2=0x00)

        # Input Source
        # self.enviacomando(6, 0x09, data0=0xAC, data1=current_input, data2=0x01, data3=0x01, data4=0x00)

        # Ahorro Energético
        self.enviacomando(6, 0x06, data0=0xD2, data1=self.db_powersavingmode)

        # One Wire
        self.enviacomando(6, 0x06, data0=0xBD, data1=self.db_onewire)

    def video_defaults(self):
        print("Reseteando opciones de vídeo...")
        try:
            self.enviacomando(6, 0x0c, data0=0x32, data1=50, data2=50, data3=50, data4=50, data5=50, data6=50, data7=1)
            print("Comando ejecutado correctamente.")
        except Exception as error:
            print(f"Se ha producido un error: {error}")

    def get_screen_version(self, print_status: int):
        # Modelo
        modelo = self.enviacomando(15, 0x06, data0=0xA1, data1=0x00)
        # Serial Code
        serialcode = self.enviacomando(19, 0x05, data0=0x15)
        # Firmware Version
        firmware = self.enviacomando(12, 0x06, data0=0xA1, data1=0x01)
        # Build Date
        build_date = self.enviacomando(15, 0x06, data0=0xA1, data1=0x02)
        # SICP Version
        sicp_version = self.enviacomando(10, 0x06, data0=0xA2, data1=0x00)
        # Platform Info
        platform_label = self.enviacomando(13, 0x06, data0=0xA2, data1=0x01)
        platform_version = self.enviacomando(8, 0x06, data0=0xA2, data1=0x02)

        # Extrae el valor que necesitamos de cada respuesta
        ext_modelo = bytes.fromhex(modelo[8:-2]).decode('utf-8')
        ext_serialcode = bytes.fromhex(serialcode[8:-2]).decode('utf-8')
        ext_firmware = bytes.fromhex(firmware[8:-2]).decode('utf-8')
        ext_sicp_version = bytes.fromhex(sicp_version[8:-2]).decode('utf-8')
        ext_platform_label = bytes.fromhex(platform_label[8:-2]).decode('utf-8')
        ext_platform_version = bytes.fromhex(platform_version[8:-2]).decode('utf-8')
        ext_build_date = bytes.fromhex(build_date[8:-2]).decode('utf-8')

        # Muestra la información por pantalla si print_status es 1
        if print_status == 1:

            print("INFORMACIÓN MONITOR")
            print(self.separador)

            tabla_version = tabulate([
                ["Modelo", ext_modelo],
                ["Número de serie", ext_serialcode],
                ["Firmware", ext_firmware],
                ["Build Date", ext_build_date],
                ["Platform Label", ext_platform_label],
                ["Platform Version", ext_platform_version],
                ["SICP Version", ext_sicp_version]
            ],
                headers=["Parámetro", "Valor"], tablefmt='orgtbl')

            print(tabla_version)

        screen_version = {'model': ext_modelo, 'serialnumber': ext_serialcode, 'firmware': ext_firmware,
                          'build_date': ext_build_date, 'platform_label': ext_platform_label,
                          'platform_version': ext_platform_version, 'sicp_version': ext_sicp_version}

        return screen_version

    def get_screen_options(self, print_status: int):
        # PowerState
        powerstate = self.enviacomando(6, 0x05, data0=0x19)
        # Boot Source
        bootsource = self.enviacomando(7, 0x05, data0=0xba)
        # Input Source
        sinput = self.enviacomando(9, 0x05, data0=0xAD)
        # Volume
        volumen = self.enviacomando(6, 0x05, data0=0x45)
        # Mute
        mute = self.enviacomando(6, 0x05, data0=0x46)

        # Power Saving Mode
        powersavingmode = self.enviacomando(6, 0x05, data0=0xD3)
        # HDMI One Wire
        onewire = self.enviacomando(6, 0x05, data0=0xbc)

        # Extrae información
        ext_volumen = int(volumen[8:10], 16)
        # Comprueba mute
        ext_mute = self.getcodevalue(mute[8:10], 5)
        # Comprueba Power
        ext_powerstate = self.getcodevalue(powerstate[8:10], 6)
        # Comprueba Power Saving Mode
        ext_powersavingmode = self.getcodevalue(powersavingmode[8:10], 2)
        # Comprueba HDMI ONE WIRE
        ext_onewire = self.getcodevalue(onewire[8:10], 3)
        # Comprueba Arranque FTE
        ext_bootsource = self.getcodevalue(bootsource[8:10], 1)
        # Comprueba Input Source
        ext_sinput = self.getcodevalue(sinput[8:10], 1)

        # Muestra la información por pantalla si print_status es 1
        if print_status == 1:
            print("PARÁMETROS MONITOR")
            print(self.separador)
            screen_table = tabulate([
                ["Power", ext_powerstate],
                ["Arranque fte", ext_bootsource],
                ["Input", ext_sinput],
                ["Volumen", ext_volumen],
                ["Mute", ext_mute],
                ["Modo ahorro", ext_powersavingmode],
                ["HDMI One Wire", ext_onewire]
                ],
                headers=["Parámetro", "Valor"], tablefmt='orgtbl')

            print(screen_table)

        screen_options = {"power": ext_powerstate, "bootsource": ext_bootsource, "input": ext_sinput,
                          "volume": ext_volumen, "mute": ext_mute, "powermode": ext_powersavingmode,
                          "onewire": ext_onewire}

        return screen_options

    def get_video_options(self, print_status: int):

        screen_settings = self.enviacomando(12, 0x0C, data0=0x33, data1=0x37, data2=0x37, data3=0x37, data4=0x37,
                                            data5=0x37,
                                            data6=0x37, data7=0x03)

        brillo = int(screen_settings[8:10], 16)  # OK
        color = int(screen_settings[10:12], 16)  # OK
        contraste = int(screen_settings[12:14], 16)  # OK
        definicion = int(screen_settings[14:16], 16)  # OK
        tono = int(screen_settings[16:18], 16)  # OK
        black_level = int(screen_settings[18:20], 16)  # OK
        gamma_select = int(screen_settings[20:22], 16)  # OK

        # Muestra la información por pantalla si print_status es 1
        if print_status == 1:
            print(self.separador)
            print("PARÁMETROS VÍDEO")
            print(self.separador)
            screen_info = tabulate([
                ["Brillo", brillo],
                ["Color", color],
                ["Contraste", contraste],
                ["Definición", definicion],
                ["Tono", tono],
                ["Nivel de negro", black_level],
                ["Gamma", gamma_select]
            ],
                headers=["Parámetro", "Valor"], tablefmt='orgtbl')

            print(screen_info)
            print(self.separador)

        listado = {"brillo": brillo, "color": color, "contraste": contraste, "definicion": definicion, "tono": tono,
                   "nivel_negro": black_level, "gamma": gamma_select}

        return listado

    def status(self, status):
        if status == "now":
            self.getscreeninfo()
            self.last_info()
        elif status == "last":
            self.last_info()

    def setpowerstatus(self, opcion):
        if opcion == "on":
            print("Encendiendo monitor...")
            self.enviacomando(6, 0x06, data0=0x18, data1=0x02)
        elif opcion == "off":
            print("Apagando monitor...")
            self.enviacomando(6, 0x06, data0=0x18, data1=0x01)

    def setvolumen(self, volumen):
        print(f"Estableciendo volumen al: {volumen}%")
        self.enviacomando(6, 0x07, data0=0x44, data1=volumen, data2=volumen)

    def setmodoahorro(self, modoahorro):
        print(f"Modificando el modo de ahorro energético: Modo {modoahorro}")
        if modoahorro == 1:
            self.enviacomando(6, 0x06, data0=0xD2, data1=0x04)
        elif modoahorro == 2:
            self.enviacomando(6, 0x06, data0=0xD2, data1=0x05)
        elif modoahorro == 3:
            self.enviacomando(6, 0x06, data0=0xD2, data1=0x06)
        elif modoahorro == 4:
            self.enviacomando(6, 0x06, data0=0xD2, data1=0x07)

    def setonewire(self, onewire):
        print(f"Configurado el modo ahorro: {onewire}")
        if onewire == "on":
            self.enviacomando(6, 0x06, data0=0xBD, data1=0x01)
        elif onewire == "off":
            self.enviacomando(6, 0x06, data0=0xBD, data1=0x00)

    def setinputsource(self, inputsource):
        print(f"Cambiando el input source a : {inputsource}")
        if inputsource.lower() == "hdmi1":
            self.enviacomando(6, 0x09, data0=0xAC, data1=0x0d, data2=0x01, data3=0x01, data4=0x00)
        elif inputsource.lower() == "hdmi2":
            self.enviacomando(6, 0x09, data0=0xAC, data1=0x06, data2=0x01, data3=0x01, data4=0x00)
        elif inputsource.lower() == "hdmi3":
            self.enviacomando(6, 0x09, data0=0xAC, data1=0x0f, data2=0x01, data3=0x01, data4=0x00)

    def setbootsource(self, bootsource):
        print(f"Configurando el arranque fte a : {bootsource}")
        if bootsource == "hdmi1":
            self.enviacomando(6, 0x07, data0=0xbb, data1=0x0d, data2=0x00)
        elif bootsource == "hdmi2":
            self.enviacomando(6, 0x07, data0=0xbb, data1=0x06, data2=0x00)
        elif bootsource == "hdmi3":
            self.enviacomando(6, 0x07, data0=0xbb, data1=0x0f, data2=0x00)

    def setmute(self, mute):
        if mute == "on":
            print("Muteando monitor...")
            self.enviacomando(6, 0x06, data0=0x47, data1=0x01)
        elif mute == 'off':
            print("Desmuteando monitor...")
            self.enviacomando(6, 0x06, data0=0x47, data1=0x00)

    def setbrillo(self, brillo):
        param = self.get_video_options(print_status=1)
        print(f"Estableciendo brillo con valor: {brillo}")
        try:
            self.enviacomando(6, 0x0c, data0=0x32, data1=brillo, data2=param['color'], data3=param['contraste'],
                              data4=param['definicion'], data5=param['tono'], data6=param['nivel_negro'], data7=param['gamma'])
            print("Configuración aplicada correctamente")

        except Exception as err:
            print(f"No se ha podido modificar el parámetro debido a un error: {err}")

    def setcontraste(self, contraste):
        param = self.get_video_options(print_status=1)
        print(f"Estableciendo contraste con valor: {contraste}")
        try:
            self.enviacomando(6, 0x0c, data0=0x32, data1=param['brillo'], data2=param['color'], data3=contraste,
                              data4=param['definicion'], data5=param['tono'], data6=param['nivel_negro'], data7=param['gamma'])
            print("Configuración aplicada correctamente")

        except Exception as err:
            print(f"No se ha podido modificar el parámetro debido a un error: {err}")


# Programa
def main():
    app = PhilipsControl()
    # Inicializa la base de datos sqlite
    app.dbcreate()

    # Argumentos CLI
    parser = argparse.ArgumentParser(description="Obtiene y modifica las opciones de los monitores Philips")
    parser.add_argument('-version', action='store_true', help="Muestra la versión del script")
    parser.add_argument('-status', type=str, choices=['now', 'last'],
                        help="Obtiene información del monitor y la muestra por pantalla")
    parser.add_argument('-power', type=str, choices=['on', 'off'], help="Enciende o apaga el monitor")
    parser.add_argument('-input', type=str, choices=['hdmi1', 'hdmi2', 'hdmi3'],
                        help="Cambia el input del monitor")
    parser.add_argument('-bootsource', type=str, choices=['hdmi1', 'hdmi2', 'hdmi3'],
                        help="Cambia el arranque fte del monitor")
    parser.add_argument('-volumen', type=int, nargs=1, help="Cambia el volumen del monitor")
    parser.add_argument('-mute', type=str, choices=['on', 'off'], help="Activa/desactiva el mute en el monitor")
    parser.add_argument('-modoahorro', type=int, nargs=1, choices=[1, 2, 3, 4],
                        help="Cambia el modo de ahorro energético del monitor")
    parser.add_argument('-onewire', type=str, choices=['on', 'off'],
                        help="Activa/Desactiva el HDMI One Wire en el monitor")
    parser.add_argument('-brillo', type=int, nargs=1, help="Cambia el brillo del monitor")
    parser.add_argument('-contraste', type=int, nargs=1, help="Cambia el contraste del monitor")
    parser.add_argument('-updateinfo', action='store_true',
                        help="Actualiza en la base de datos la información actual del monitor")
    parser.add_argument('-autosetup', action='store_true',
                        help="Aplica la configuración al monitor en función de su modelo")
    parser.add_argument('-restorevideo', action='store_true',
                        help='Resetea los valores de vídeo a 50 (brillo, contraste, color, tono, etc.)')
    parser.add_argument('-query', nargs='*', help="Realiza una consulta a la base de datos")

    args = parser.parse_args()

    if args.status:
        app.status(args.status)
        # app.getscreeninfo()

    if args.version:
        print(app.sw_version)

    if args.power:
        app.setpowerstatus(args.power)

    if args.volumen:
        app.setvolumen(args.volumen[0])

    if args.modoahorro:
        app.setmodoahorro(args.modoahorro[0])

    if args.onewire:
        app.setonewire(args.onewire)

    if args.input:
        app.setinputsource(args.input)

    if args.bootsource:
        app.setbootsource(args.bootsource)

    if args.mute:
        app.setmute(args.mute)

    if args.autosetup:
        app.autoscreensetup()

    if args.restorevideo:
        app.video_defaults()

    if args.updateinfo:
        app.getscreeninfo()

    if args.query:
        app.select_query(' '.join(str(x) for x in args.query))

    if args.brillo:
        app.setbrillo(args.brillo[0])

    if args.contraste:
        app.setcontraste(args.contraste[0])

    app.con.close()


if __name__ == "__main__":
    main()
