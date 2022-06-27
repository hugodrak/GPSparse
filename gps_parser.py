import serial # pyserial
import os
import time
from threading import Thread

def pretty_printer(vals):
    #[["a","ddddddee"], ["aaa", "bbbb"]]
    out = []
    maxbef = len(max(vals, key=lambda b:len(b[0]))[0])
    maxval = len(str(max(vals, key=lambda b:len(str(b[1])))[1]))
    maxun = len(max(vals, key=lambda b:len(b[2]))[2])
    out.append(f"┌{'─'*maxbef}┬{'─'*maxval}┬{'─'*maxun}┐")
    for bef, val, un in vals:
        out.append(f"│{bef.rjust(maxbef)}│{str(val).rjust(maxval)}│{un.rjust(maxun)}│")

    out.append(f"└{'─'*maxbef}┴{'─'*maxval}┴{'─'*maxun}┘")

    return "\n".join(out) + "\n\n"



def float_form(string, leng):
    if string:
        return round(float(string), leng)
    return 0.

def ll_form(string, leng):
    if string:
        ss = string.split(".")
        return round(float(ss[0][:-2]) + float(f"{ss[0][-2:]}.{ss[1]}")/60., leng)

    return 0.

def int_form(string):
    if string:
        return int(string)
    return 0


class GPGGA:
    def __init__(self):
        self.utctime = ""
        self.latitude = 0.
        self.north_south = "N"
        self.longitude = 0.
        self.east_west = "E"
        self.pos_fix_indicator = 1 # 0:fix N/A, 1: GPS SPS mode, 2:diff GPS, 6:dead reckoning
        self.satellites_used = 0
        self.hdop = 0.
        self.msl_alt = 0. #meters
        self.units = ""
        self.geoid_separation = 0. # meters
        self.age_of_diff_corr = 0
        self.diff_ref_station = ""
        self.checksum = ""

    def update(self, line):
        # strings
        self.utctime = line[1]
        self.north_south = line[4]
        self.east_west = line[6]
        self.units = line[10]
        self.checksum = line[14].split("*")[1]

        #ints
        if val := int(line[6]) in [0,1,2,6]:
            self.pos_fix_indicator = val
        self.age_of_diff_corr = int_form(line[13])

        #floats
        self.latitude = ll_form(line[2], 6)
        self.longitude = ll_form(line[4], 6)
        self.hdop = float_form(line[8], 2)
        self.msl_alt = float_form(line[9], 2)
        self.geoid_separation = float_form(line[11], 2) # meters

    def __repr__(self):
        vals = [["GPGGA", "", ""], ["UTC time", self.utctime, "hhmmss"], ["Unit", self.units, ""], ["Diff corr age", self.age_of_diff_corr, "sec"],
        ["Lat", self.latitude, self.north_south], ["Long", self.longitude, self.east_west]]
        return pretty_printer(vals)



class GPRMC:
    def __init__(self):
        self.utctime = ""
        self.status = ""
        self.latitude = 0.
        self.north_south = "N"
        self.longitude = 0.
        self.east_west = "E"
        self.SOG = 0. # knots
        self.COG = 0. #course, deg
        self.date = ""
        self.mag_var = 0. #deg
        self.mode = "" # A: autonomous, D: DGPS, E:DR
        self.checksum = ""

    def update(self, line):
        #print(line)
        # strings
        self.utctime = line[1]
        self.status = line[2]
        self.north_south = line[4]
        self.east_west = line[6]
        self.date = line[9]
        self.checksum = line[12]
        #floats
        self.latitude = ll_form(line[3], 6)
        self.longitude = ll_form(line[5], 6)
        self.SOG = float_form(line[7],3) # knots
        self.COG = float_form(line[8],3) #course, deg
        self.mag_var = float_form(line[10],3) #deg

    def __repr__(self):
        vals = [["GPRMC", "", ""], ["UTC time", self.utctime, "hhmmss"], ["Date", self.date, ""], ["Speed over ground", self.SOG, "knots"], ["Course over ground", self.COG, "deg"],
        ["Lat", self.latitude, self.north_south], ["Long", self.longitude, self.east_west]]
        return pretty_printer(vals)




class GPSdata:
    def __init__(self):
        self.GGA = GPGGA()
        #self.GSA
        #self.GSV
        self.RMC = GPRMC()

        self.lat = 0.0
        self.lon = 0.0
        self.timestamp = 0
        self.course = 0.0
        self.satelites = 0
        self.speed = 0.0
        self.active = False

    def update(self, line):
        id = line[3:8]
        data_line = line.split(",")
        if not self.active:
            if id == "GPRMC":
                if data_line[2] == "A":
                    self.active = True
        else:
            if id == "GPRMC":
                self.RMC.update(data_line)
            elif id == "GPGGA":
                self.GGA.update(data_line)


class GPSreader(Thread):
    def __init__(self, port, speed, data):
        Thread.__init__(self)
        self.running = True

        self.conn = serial.Serial(port, speed)
        self.data = data

    def run(self):
        while self.running:
            line = str(self.conn.readline()).replace("\\r\\n", "")
            self.data.update(line)
            time.sleep(1)

    def stop(self):
        self.running = False





def setup_logdir():
    if "logs" not in os.listdir("."):
        os.mkdir("./logs")
    return True


class Connection:
    def __init__(self, port):
        self.speed = 4800
        self.port = port
        #self.connection = serial.Serial(port, self.speed)
        setup_logdir()
        self.logpath = f"./logs/GPSLOG_{time.time()}.csv"
        self.logfile = open(self.logpath, "w")
        self.GPS_thread = None
        self.data = GPSdata()

    def start(self):
        self.GPS_thread = GPSreader(self.port, self.speed, self.data)
        self.GPS_thread.start()

    def stop(self):
        print("trying stop")
        self.GPS_thread.stop()

    def print_data(self):
        if self.data.active:
            print(self.data.GGA)
            print(self.data.RMC)
#        rmc = self.data.RMC
        # out = {"lat:":rmc.latitude, "lon:":rmc.longitude,
        # "COG:":rmc.COG, "SOG:":rmc.SOG, "satellites:":0,
        # "magvar:": rmc.mag_var, "UTC:": rmc.utctime, "stat:": rmc.status,
        # "NS": rmc.north_south, "EW:": rmc.east_west, "date": rmc.date,
        # "chekc": rmc.checksum}
        # print(out)
