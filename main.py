import serial
import time
import os
import sys
import re
logs = 0
for file in os.listdir("./logs/"):
    if file.endswith(".csv"):
        logs += 1

FILE_NAME = "./logs/%s.csv"%str(logs+1)
SERIAL_PATH = sys.argv[1]
print("Log file:", FILE_NAME)

open(FILE_NAME, "w").write("logCreationTime:"+str(round(time.time()))+"\n")
ser = serial.Serial(SERIAL_PATH, 4800)

def get_data(compares):
    keep_searching = True
    sufficient = {}
    data = {'GPGSA': [], 'GPGSV': [], 'GPRMC': [], 'GPGGA': []}

    while keep_searching:
        line = str(ser.readline())
        identifier = line[2:8]
        print(line)
        if identifier == "$GPGSA":
            data['GPGSA'].append(line.split(','))
        if identifier == "$GPGGA":
            data['GPGGA'].append(line.split(','))
        if identifier == "$GPRMC":
            data['GPRMC'].append(line.split(','))
        if identifier == "$GPRSV":
            data['GPGSA'].append(line.split(','))

        for key, value in data.items():
            if compares <= len(value):
                sufficient[key] = ""

        if len(sufficient) == 3:
            keep_searching = False
            break

    # parsed_data = {'time': 0.0, 'lat': 0.0, 'long':0.0, 'speed': 0.0, 'course': 0.0}
    parsed_data = [0.0, 0.0, 0.0, 0.0, 0.0]

    for key, value in data.items():
        for v in value:
            # if v[0] == "b'$GPGSA":
            #     _ = ""
            # if v[0] == "b'$GPGGA":
            #     _ = 0

            # Currently only using GPRMC
            if v[0] == "b'$GPRMC":

                # A is valid, V-invalid
                if v[2] == "A":
                    # Time rounded to int
                    if parsed_data[0] > 0:
                        parsed_data[0] = round((parsed_data[0]+float(v[1]))/2)
                    else:
                        parsed_data[0] = round(float(v[1]))

                    # Latitude rounded to 6 decimals
                    if parsed_data[1] > 0:
                        lat_sp = v[3].split(".")
                        parsed_data[1] = round(float(lat_sp[0][:-2]) + float(f"{lat_sp[0][-2:]}.{lat_sp[1]}"),6)
                        #parsed_data[1] = round((parsed_data[1]+float(v[3])*0.01)/2, 6)
                    else:
                        parsed_data[1] = round(float(v[3])*0.01, 6)

                    # Longitude rounded to 6 decimals
                    if parsed_data[2] > 0:
                        parsed_data[2] = round((parsed_data[2]+float(v[5])*0.01)/2, 6)
                    else:
                        parsed_data[2] = round(float(v[5])*0.01, 6)

                    # Speed in Knot => metres per second, rounded to 2 decimals
                    if parsed_data[3] > 0:
                        parsed_data[3] = round((parsed_data[3]+float(v[7])*0.5144447)/2, 2)
                    else:
                        parsed_data[3] = round(float(v[7])*0.5144447, 2)

                    # Course rounded to 1 decimal
                    if parsed_data[4] > 0:
                        parsed_data[4] = round((parsed_data[4]+float(v[8]))/2, 1)
                    else:
                        parsed_data[4] = round(float(v[8]), 1)
                else:
                    print("No Connection! Status: V, Sleeping 20s")
                    time.sleep(20)
                    return []
    return parsed_data

while True:
    file = open(FILE_NAME, "a")
    file.write(','.join(map(str, get_data(3))))
    file.write("\n")
    file.close()
    # time.sleep(2)
