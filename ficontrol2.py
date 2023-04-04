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
        self.sw_version = "v1.1 2023/03/28"
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
        self.db_powersavingmode = ""
        self.db_onewire = ""

        # Se añaden las variables control y grupo al contructor
        self.control = 0x01
        self.group = 0x00

    @staticmethod
    def str2hex(string_):
        base16 = int(string_, 16)
        hex_value = hex(base16)
        return hex_value

    def enviacomando(self, timeout, msg_size, **kwargs):

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
        ser.close()
        return res.hex()

    def dbcreate(self):
        if os.path.exists(self.dbpath):
            pass
        else:
            os.mkdir(self.dbpath)
        self.cur.execute("PRAGMA foreign_keys = ON")

        self.cur.execute("CREATE TABLE IF NOT EXISTS screeninfo("
                         "id integer primary key autoincrement,"
                         "modelname text,"
                         "serialnumber text,"
                         "fwversion text,"
                         "build_date text,"
                         "date_mod date)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS screenconfig("
                         "model text NOT NULL ,"
                         "bootsource text,"
                         "inputsource text,"
                         "powersavingmode text,"
                         "onewire text)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS idgrupos("
                         "id integer primary key autoincrement ,"
                         "name text NOT NULL"
                         ")")

        self.cur.execute("CREATE TABLE IF NOT EXISTS codigos("
                         "id integer primary key autoincrement, "
                         "idtype integer NOT NULL,"
                         "codename text,"
                         "hexcode text,"
                         "foreign key (idtype) references idgrupos(id))")

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
        print("Registrando datos en la bbdd...")
        ask_modelo = self.enviacomando(15, 0x06, data0=0xA1, data1=0x00)
        modelo = bytes.fromhex(ask_modelo[8:-2]).decode('utf-8')

        ask_serialcode = self.enviacomando(19, 0x05, data0=0x15)
        serialcode = bytes.fromhex(ask_serialcode[8:-2]).decode('utf-8')

        self.cur.execute("SELECT DATETIME('now', 'localtime')")
        localtime_date = self.cur.fetchone()[0]

        self.cur.execute(f"INSERT INTO screeninfo(modelname, serialnumber, date_mod) VALUES"
                         f" ('{modelo}', '{serialcode}', '{localtime_date}')")
        self.con.commit()

    def autoscreensetup(self):
        # Configura la pantalla en función de su modelo, aplica las configuraciones que tiene almacenadas en BBDD.
        print("Configurando monitor...")
        # Obtiene el modelo del monitor
        ask_modelo = self.enviacomando(15, 0x06, data0=0xA1, data1=0x00)
        modelo_monitor = bytes.fromhex(ask_modelo[8:-2]).decode('utf-8')

        # Obtiene el input que tiene configurado actualmente
        current_input = self.enviacomando(9, 0x05, data0=0xAD)

        # Selecciona la configuración en función del modelo del monitor
        self.cur.execute(f"""SELECT * from screenconfig WHERE model= '{modelo_monitor}'""")
        rows = self.cur.fetchall()
        for row in rows:
            self.db_modelo = row[0]
            self.db_powersavingmode = int(row[3], 16)
            self.db_onewire = int(row[4], 16)

        # Aplica la configuración según el modelo
        # Arranque Fte.
        self.enviacomando(6, 0x07, data0=0xbb, data1=int(current_input[8:10], 16), data2=0x00)
        # Input Source
        # self.enviacomando(6, 0x09, data0=0xAC, data1=current_input, data2=0x01, data3=0x01, data4=0x00)
        # Ahorro Energético
        self.enviacomando(6, 0x06, data0=0xD2, data1=self.db_powersavingmode)
        # One Wire
        self.enviacomando(6, 0x06, data0=0xBD, data1=self.db_onewire)

    def status(self):
        print("Obteniendo información del monitor...")
        # Modelo
        modelo = self.enviacomando(15, 0x06, data0=0xA1, data1=0x00)
        # Serial Code
        serialcode = self.enviacomando(19, 0x05, data0=0x15)
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
        # Screen info
        screen = self.enviacomando(12, 0x0C, data0=0x33, data1=0x37, data2=0x37, data3=0x37, data4=0x37, data5=0x37,
                                   data6=0x37, data7=0x03)
        # Power Saving Mode
        powersavingmode = self.enviacomando(6, 0x05, data0=0xD3)
        # HDMI One Wire
        onewire = self.enviacomando(6, 0x05, data0=0xbc)

        # Extrae el valor que necesitamos de cada respuesta
        ext_modelo = bytes.fromhex(modelo[8:-2]).decode('utf-8')
        ext_serialcode = bytes.fromhex(serialcode[8:-2]).decode('utf-8')
        ext_volumen = int(volumen[8:10], 16)
        ext_brillo = int(screen[8:10], 16)

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

        # Muestra la información por pantalla
        tabla = tabulate([
            ["Modelo", ext_modelo],
            ["Número de serie", ext_serialcode],
            ["Power", ext_powerstate],
            ["Arranque fte", ext_bootsource],
            ["Input", ext_sinput],
            ["Volumen", ext_volumen],
            ["Mute", ext_mute],
            ["Brillo", ext_brillo],
            ["Modo ahorro", ext_powersavingmode],
            ["HDMI One Wire", ext_onewire]
            ],
            headers=["Parámetro", "Valor"], tablefmt='orgtbl')

        print(tabla)

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


# Programa
def main():
    app = PhilipsControl()
    # Inicializa la base de datos sqlite
    app.dbcreate()

    # Argumentos CLI
    parser = argparse.ArgumentParser(description="Obtiene y modifica las opciones de los monitores Philips")
    parser.add_argument('-version', action='store_true', help="Muestra la versión del script")
    parser.add_argument('-status', action='store_true', help="Obtiene información del monitor")
    parser.add_argument('-power', type=str, choices=['on', 'off'], help="Enciende o apaga el monitor")
    parser.add_argument('-input', type=str, choices=['hdmi1', 'hdmi2', 'hdmi3'],
                        help="Cambia el input del monitor")
    parser.add_argument('-volumen', type=int, nargs=1, help="Cambia el volumen del monitor")
    parser.add_argument('-modoahorro', type=int, nargs=1, choices=[1, 2, 3, 4],
                        help="Cambia el modo de ahorro energético del monitor")
    parser.add_argument('-onewire', type=str, choices=['on', 'off'],
                        help="Activa/Desactiva el HDMI One Wire en el monitor")
    parser.add_argument('-bootsource', type=str, choices=['hdmi1', 'hdmi2', 'hdmi3'],
                        help="Cambia el arranque fte del monitor")
    parser.add_argument('-mute', type=str, choices=['on', 'off'], help="Activa/desactiva el mute en el monitor")
    parser.add_argument('-autosetup', action='store_true',
                        help="Aplica la configuración al monitor en función de su modelo")
    parser.add_argument('-saveinfo', action='store_true',
                        help="Registra en la base de datos la información del monitor (modelo, s/n, firmware)")
    parser.add_argument('-query', nargs='*', help="Realiza una consulta a la base de datos")

    args = parser.parse_args()

    if args.status:
        app.status()
        app.getscreeninfo()

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

    if args.saveinfo:
        app.getscreeninfo()

    if args.query:
        app.select_query(' '.join(str(x) for x in args.query))

    app.con.close()


if __name__ == "__main__":
    main()
