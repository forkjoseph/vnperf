#!/usr/bin/env python

import serial, sys
DEV = '/dev/ttyUSB0'

def get_loc(ser, oldlat, oldlon):
    lat = oldlat
    lon = oldlon
    sline = ser.readline().split(',')

    if sline[0] == '$GPGGA':
        latRaw = sline[2]
        latDir = sline[3]
        lonRaw = sline[4]
        lonDir = sline[5]

        latDeg = int(float(latRaw)) / 100
        latMin = float(latRaw) - (latDeg * 100)
        latMin /= 60.0
        lat = latDeg + latMin

        lonDeg = int(float(lonRaw)) / 100
        lonMin = float(lonRaw) - (lonDeg * 100)
        lonMin /= 60.0
        lon = lonDeg + lonMin
 

        if latDir == 'S':
            lat *= -1
        if lonDir == 'W':
            lon *= -1

        oldlat = lat
        oldlon = lon
    else:
        lat = oldlat
        lon = oldlon
    return (lat, lon)


if __name__ == '__main__':
    if sys.argv[1]:
        DEV='/dev/tty' + (sys.argv[1]).upper()
    ser = serial.Serial(DEV, 4800, timeout=5)

    oldlat = 0
    oldlon = 0

    while True:
        lat, lon = get_loc(ser, oldlat, oldlon)
        print "%f, %f" % (lat, lon)

        oldlat = lat
        oldlon = lon
