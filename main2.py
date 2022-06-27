from gps_parser import Connection
import time

cn = Connection("/dev/ttyUSB0")
cn.start()
print("started  ")
while True:
    try:
        cn.print_data()
        time.sleep(2)
    except KeyboardInterrupt as exc:
        cn.stop()
        break
#cn.stop()
