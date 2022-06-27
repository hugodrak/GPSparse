# GPSparse
A simple interface for serial NMEA standard usb GPS.
---
Usage:

from gps_parser import Connection

cn = Connection("/dev/ttyUSB0")

cn.start()

NMEA docs:
https://www.sparkfun.com/datasheets/GPS/NMEA%20Reference%20Manual-Rev2.1-Dec07.pdf
