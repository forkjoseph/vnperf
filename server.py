#!/usr/bin/env python
import socket
import errno
import logging
import platform
import signal
import sys
import threading
import time
from threading import Thread
import fcntl
import struct
from netifaces import AF_INET, AF_INET6, AF_LINK

IFACE = 'eth0'
TCP_PORT = 4301
MESSAGE = 'pong-{:05d}'
BUFFER_SIZE = len('pong-00000')
threads = []

def sighand(signal, frame):
    logging.info('Quitting...')
    for t in threads:
        t.join()
    sys.exit(0)
    return

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

def club_waiter(conn, addr):
    logging.info('Incoming: %s' % (str(addr)))
    cnt = 0
    while True:
        try:
            conn.settimeout(0) # 120.0)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            data = conn.recv(BUFFER_SIZE)
            if not data:
                raise Exception('Client disconnected ' + str(addr))
            target_cnt = int(data.split('-')[1])
            # DEBUG
            sent = conn.send(MESSAGE.format(target_cnt))
            if len(data) != sent:
                raise Exception('Client disconnected ' + str(addr))

            cnt = cnt + 1
            print addr, target_cnt
        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                # print 'no data available yet'
                continue
            else:
                logging.error(e)
                conn.close()
                return False
        except Exception as e:
            logging.error(e)
            conn.close()
            return False
    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='.server.log',
            format='%(asctime)s %(levelname)s:%(message)s')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    TCP_IP  = get_ip_address(IFACE)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(10)

    while 1:
        conn, addr = s.accept()
        t = Thread(target=club_waiter, args = (conn, addr,))
        threads.append(t)
        t.start()
