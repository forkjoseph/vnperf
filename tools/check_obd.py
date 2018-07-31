#!/usr/bin/env python

import obd, sys, time, serial
from obd import *
DEV = '/dev/ttyUSB1'

def get_mph(obd_con):
    mph = -1.0
    response = obd_con.query(obd.commands.SPEED)
    if response.value is not None:
        mph = response.value.to('mph')
        mph = float(str(mph).split(' ')[0])
    return mph


if __name__ == '__main__':
    if sys.argv[1]:
        DEV='/dev/tty' + (sys.argv[1]).upper()

    obd_con = obd.OBD(DEV)


    while obd_con.status() != OBDStatus.CAR_CONNECTED:
        obd_con = obd.OBD(DEV)
        time.sleep(0.1)

    while True:
        mph = get_mph(obd_con)
        print mph
        time.sleep(1)
