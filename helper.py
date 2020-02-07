import os.path
import errno
import argparse
import logging
from datetime import datetime as dt
import obd, serial
import socket
from netifaces import AF_INET, AF_INET6, AF_LINK
import struct, fcntl
import platform, sys

# [CUSTOM] 
from config import *

parser = argparse.ArgumentParser(description='RTT measure')
parser.add_argument('-i', '--interfaces', default=[], required=True,
        action='append', type=str, help='Interface to be used')
parser.add_argument('-t', '--target_servers', default=[], required=True,
        action='append', type=str, help='Target server to measure RTT')
parser.add_argument('-n', '--numruns', type=int, help='How many runs?')
parser.add_argument('-o', '--output', default='log/rtt.txt', type=str, help='')
parser.add_argument('-H', '--howlong', type=int, help='How long to run')
parser.add_argument('-I', '--interval', default=1.0, type=float, help='Interval')
parser.add_argument('-D', '--debug', action='store_true')
parser.add_argument('-P', '--powertest', action='store_true')
args = parser.parse_args()

class StaticConfig:
    interface_order = ['usb0', 'usb1', 'usb2', 'wlan1', 'wlan0', 'eth0']
    elems = ['thread', 'thread_name', 'socket', 'ipaddr', 'interface', 'target',
            'current_cnt', 'rttqueue',]

def dircheck(tmpdir):
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    return

def init_logger(level=logging.INFO):
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s: %(message)s'
    dtfmt = '%H:%M:%S'

    if args.debug:
        level=logging.DEBUG
    logFormatter = logging.Formatter(fmt=fmt, datefmt=dtfmt)
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level)

    fileHandler = logging.FileHandler('.client.log')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    logging.info(''.join('=' for i in range(55)))
    logging.info('Start of logging at %s' % (dt.now()))
    logging.info(''.join('=' for i in range(55)))

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    return

def init_config(LOG_GPS=True, LOG_OBD=True):
    config = Config
    if not LOG_GPS:
        config.LOG_GPS = False
    else:
        if os.path.exists(config.DEV_GPS):
            config.LOG_GPS = True
        else:
            config.LOG_GPS = False

    if not LOG_OBD:
        config.LOG_OBD = False
    else:
        if os.path.exists(config.DEV_OBD):
            config.LOG_OBD = True
        else:
            config.LOG_OBD = False

    if config.LOG_GPS:
        config.con_gps = serial.Serial(config.DEV_GPS, 4800, timeout=20)

    if config.LOG_OBD:
        config.con_obd = obd.OBD(config.DEV_OBD)
    
    if args.interval:
        config.INTERVAL = args.interval
    if args.output:
        config.OUTPUT_FILENAME = args.output

    if args.howlong and args.numruns:
        print '[ERROR] cannot define howlong and numruns at same time!'
    else:
        if args.howlong:
            config.HOWLONG = args.howlong
            config.numruns = int(config.HOWLONG / config.INTERVAL)
        elif args.numruns:
            config.numruns = args.numruns

    if args.powertest:
        config.PWTEST_MODE = True

    for iface in args.interfaces:
        config.ifaces.append(iface)
    for target in args.target_servers:
        config.targets.append(target)

    config.logfile = open(config.OUTPUT_FILENAME, 'a+')

    logging.debug('Done init config!')
    if config.PWTEST_MODE:
        logging.debug("***** running power test version.... ******** ")
    logging.debug('%10s: %s' % ('OBD', config.LOG_GPS))
    logging.debug('%10s: %s' % ('GPS', config.LOG_OBD))
    logging.debug('%10s: %.3f sec' % ('How Long', config.HOWLONG))
    logging.debug('%10s: %.3f sec' % ('Interval', config.INTERVAL))
    logging.debug('%10s: %.3f run' % ('How Many', config.numruns))
    return config

def get_mph(config):
    if config.LOG_OBD is False:
        return -1.0
    if config.con_obd is None:
        return -1.0
    response = config.con_obd.query(obd.commands.SPEED)
    if response.value is not None:
        mph = response.value.to('mph')
        mph = float(str(mph).split(' ')[0])
        return mph
    return -1.0

def get_loc(config, oldlat, oldlon):
    if config.LOG_GPS is False:
        return (oldlat, oldlon)
    if config.con_gps is None:
        return (oldlat, oldlon)
    lat = oldlat
    lon = oldlon
    sline = config.con_gps.readline().split(',')
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
    return (lat, lon)

def get_ip_address(ifname):
    try:
        if platform.system() == 'Linux':
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, \
                    struct.pack('256s', ifname[:15]))[20:24])
        elif platform.system() == 'Darwin': # mac
            return netifaces.ifaddresses(ifname)[AF_INET][0]['addr']
    except IOError as e:
        logging.error('[get_ipaddr] %s (%s)' % (str(e), ifname))
        raise e
    return None

# socket stuff
# @return: established socket if successful
def get_connected(interface, ipaddr, target):
    if not ipaddr: 
        return None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((ipaddr, 0))
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        s.settimeout(5)

        s.connect((target, TCP_PORT))
        s.settimeout(0.0) # non-blocking
    except IOError as e:
        logging.error('[get_connected] %s (%s => %s)' % (str(e), str(ipaddr), \
            str(target)))
        s = None
        raise e
    except Exception as e:
        logging.error('[get_connected] %s (%s => %s)' % (str(e), str(ipaddr), \
            str(target)))
        s = None
        raise e
    return s

def load_servers(fname="targetservers.txt"):
    import os.path
    exists = os.path.isfile(fname) 
    if exists is False:
        raise Exception("You must define target servers!!")

    server_order = []
    with open(fname) as f:
        lines = f.readlines()
        for l in lines:
            if l.startswith('#'): 
                continue
            l = l.strip()
            server_order.append(l)
    return server_order

