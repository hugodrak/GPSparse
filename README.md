# GPSparse
A simple interface for serial NMEA standard usb GPS.
---
Usage:

from gps_parser import Connection

cn = Connection("/dev/ttyUSB0")
cn.start()
