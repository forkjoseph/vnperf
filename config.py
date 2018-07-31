# config.py
TCP_PORT = 4301
MESSAGE = "ping-{:05d}"
BUFFER_SIZE = len('ping-00000')

class Config:
    DEV_GPS = '/dev/ttyUSB1'
    DEV_OBD = '/dev/ttyUSB0'

    LOG_GPS = False
    LOG_OBD = False
    
    PWTEST_MODE = False

    INTERVAL = 1.0
    OUTPUT_FILENAME = 'rtt.csv'
    HOWLONG = 5 # in secs
    numruns = 5

    ifaces = []
    targets = []

    con_gps = None
    con_obd = None
    logfile = None
