#!/usr/bin/env python2.7
import os, sys, signal
import copy
import time

from collections import OrderedDict
from threading import Thread, Lock, Semaphore, RLock
from Queue import Queue
from multiprocessing import Process, Lock
import multiprocessing.pool as mpp
import multiprocessing

# [CUSTOM] 
from helper import *

config = None

server_order = ['127.0.0.1', ] # '141.212.110.34', '141.212.110.236', '52.14.177.151']
interface_order = ['usb0', 'usb1', 'wlan1', 'wlan0', 'eth0']

elems = ['thread', 'thread_name', 'socket', 'ipaddr', 'interface', 'target',
        'current_cnt', 'rttqueue',]
template = dict((elem, None) for elem in elems)
rtts = {'wlan0': {}, 'wlan1' : {}, 'usb0': {}, 'usb1': {}, 'eth0': {}, }
global_m = []
must_have = []
# must_have = ['{:s}-{:s}'.format(intf, tg)
#             for intf in interface_order for tg in server_order
#             if intf in args.interfaces and tg in args.target_servers ]
runs = {}
pool = None
infos = []
logmonitor = None
terminate = False
is_terminated = False
current_ap = {'wlan0': None, 'wlan1': None}
wlandict = {'wlan0' : {'141.212.110.34': 0, '141.212.110.236': 0}, 
        'wlan1': {'141.212.110.34': 0, '141.212.110.236': 0}}
current_cnt = 0

###############################################################################
# helpers
###############################################################################
def signal_handler(signal, frame):
    global pool, logmonitor
    global terminate, is_terminated
    global config

    logging.debug('You pressed Ctrl+C! (pid %d, ppid %d)' % (os.getpid(), \
        os.getppid()))

    terminate = True
    log_commit()
    is_terminated = True

    pool.terminate()
    pool.join()
    logmonitor.join()
    sys.exit(0)

###############################################################################
# measures [worker pool]
###############################################################################
def rtt_worker(info):
    # name := target + '-' + cnt
    global current_cnt, terminate, is_terminated
    global wlandict
    sck = info['socket']
    cnt = current_cnt 
    has_sent = False
    wlan1lock = info['wlan1lock']

    interface = info['interface']
    target = info['target']
    name = target + '-' + str(cnt)
    queue = info['rttqueue']
    if interface.startswith('wlan'):
        wlancnt = wlandict[interface][target]

    ret = {'cnt' : cnt, 'interface': interface,
            'ipaddr' : info['ipaddr'], 'target' : info['target'], 
            'start_ts': None, 'end_ts' : None, }

    if interface.startswith('wlan'):
        ret['send_ap'] = None
        ret['recv_ap'] = None

    counter = 0
    if sck is None:
        return ret

    ret['start_ts'] = dt.now()
    rtts[interface][name] = copy.deepcopy(ret)

    while True:
        try:
            counter += 1
            if has_sent is False:
                send_data = MESSAGE.format(cnt)
                # if interface.startswith('wlan'):
                #     if wlancnt > 4:
                #         print 'deletig...!', name, wlancnt
                #         del rtts[interface][name]
                #         return
                #     else:
                #         with wlan1lock:
                #             wlandict[interface][target] += 1
                sent = sck.send(send_data)

                # print 'Has been sent', cnt, sent, ret
            if sent > 0:
                has_sent = True

            # give 10 seconds to clean up
            if terminate or is_terminated:
                diff = dt.now() - ret['start_ts']
                if diff.seconds > 25:
                    logging.debug('Terminating... %d for %s to %s' % \
                            (cnt, interface, target))
                    break

            recv_data = sck.recv(BUFFER_SIZE)
            if len(send_data) == len(recv_data):
                end = dt.now()
                recv_cnt = int(recv_data.split('-')[1])
                if interface.startswith('wlan'):
                    with wlan1lock:
                        wlandict[interface][target] -= 1

                if cnt == recv_cnt:
                    has_sent = False
                    ret['end_ts'] = end
                    ret['ofo'] = False
                    rtts[info['interface']][name]['end_ts'] = end
                    rtts[info['interface']][name]['ofo'] = False
                    queue.put_nowait(rtts[info['interface']][name])
                    break
                else: # out-of-order pongs
                    # print send_data, recv_data, cnt, recv_cnt
                    correct_name = info['target'] + '-' + str(recv_cnt)
                    rtts[info['interface']][correct_name]['end_ts'] = end
                    rtts[info['interface']][correct_name]['ofo'] = True
                    queue.put_nowait(rtts[info['interface']][correct_name])
                    ret = rtts[info['interface']][correct_name]
                    logging.debug('ofo by %d] %d (%s -> %s)' % \
                            (cnt, recv_cnt, interface, target))
                    break
            elif len(recv_data) > 0:
                logging.debug('cnt > 0, %d, %d, %d' % (cnt, send_data, recv_cnt))

        except socket.error, e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                if counter > 100:
                    time.sleep(0.001) # 1 nsec
                continue
            else:
                logging.error('errorr..... %s' % (str(e)))
                # sck.close()
                raise e
        except Exception as e:
            logging.error('error2..... %s' % (str(e)))
            sck.close()
            raise e
    return ret

def donedone(m):
    # tup = m[0]
    # cnt = tup['cnt']
    # src = tup['interface']
    # dst = tup['target']
    # rtt = log_compute_delta(tup)
    # print 'is ofo?', tup['ofo']
    # print cnt, src, dst, rtt
    # log_commit_at(at=cnt)
    return

###############################################################################
# Trace related [thread]
###############################################################################
def log_commit_this(meta, vals):
    global config
# PWTEST_MODE
    tmp = '{:3d},{:10s}'
    if config.logfile.closed:
        config.logfile = open(config.logfile.name, 'a+')

    mcnt, ts, mph, lat, lon = meta
    if config.LOG_OBD:
        tmp += ',{:6.3f}'.format(mph)
    if config.LOG_GPS:
        tmp += ',{:10.6f},{:10.6f}'.format(lat, lon)
    if config.PWTEST_MODE:
        tmp += ',{:.0f}'.format(config.INTERVAL)

    config.logfile.write(tmp.format(mcnt, ts))
    for name in must_have:
        m = vals[name]
        config.logfile.write(',{:.3f}'.format(m))
    config.logfile.write('\n')
    config.logfile.flush()
    os.fsync(config.logfile.fileno())
    return

def log_monitor(rttqueue):
    global current_cnt, global_m, runs, must_have
    global terminate, is_terminated
    global config

    log_build_hdr()
    expected_runs = config.numruns
    counter = 0
    prev_current_cnt = 0

    while True:
        cSize = rttqueue.qsize()
        if cSize == 0:
            sleep = config.INTERVAL * counter
            # logging.debug('sleeping for %f' % sleep)
            time.sleep(sleep) # exp. sleep
            counter += 1 
            if is_terminated:
                logging.info('terminated at %d' % current_cnt)
                break

            if counter > 25 and expected_runs <= current_cnt:
                logging.info('break at %d' % current_cnt)
                break
        else:
            counter = 1
            rtt = rttqueue.get()
            m = log_compute_delta(rtt)
            name = rtt['interface'] + '-' + rtt['target']
            cnt = rtt['cnt'] 
            # print 'RTT....', rttqueue.qsize(), cnt, name, m
            try:
                obj = runs[cnt]
            except KeyError as e:
                runs[cnt] = {}
                obj = {}
            
            try:
                obj[name] = m
            except KeyError as e:
                logging.error('errrrrrrrrrrrr %s' % (str(e)))
            runs[cnt] = obj

        if (current_cnt != prev_current_cnt):
            log_print()
            log_commit_at()
            prev_current_cnt = current_cnt

    logging.info('no more runs! [queue size %d, runs %d, current %d]' % \
            ( rttqueue.qsize(), expected_runs, current_cnt))

# for sync...
    while rttqueue.qsize() > 0:
        rtt = rttqueue.get()
        m = log_compute_delta(rtt)
        name = rtt['interface'] + '-' + rtt['target']
        cnt = rtt['cnt'] 
        # print 'RTT....', rttqueue.qsize(), cnt, name, m
        try:
            obj = runs[cnt]
        except KeyError as e:
            runs[cnt] = {}
            obj = {}
        
        try:
            obj[name] = m
        except KeyError as e:
            logging.error('errrrrrrrrrrrr %s' % (str(e)))
        runs[cnt] = obj

    # if is_terminated is False:
    while is_terminated is False:
        print 'commiting log...!'
        log_commit()
        time.sleep(1)

    if rttqueue.qsize() != 0:
        logging.debug('Queue is NOT empty! make sure to cleanup properly')

    return

def log_commit_at(at=-1, rollback=5):
    global current_cnt, global_m, runs, must_have

    if at > -1:
        try:
            print runs
            vals = runs[at]
            print vals
            keys = vals.keys()
            for check in must_have:
                if check not in keys:
                    vals[check] = -1.0
            idx = at - 1
            log_commit_this(global_m[idx], vals)
        except Exception as e:
            print 'DNE error...', e
    else:
        max_cnt = -1
        for cnt, vals in runs.iteritems():
            keys = vals.keys()
            for check in must_have:
                if check not in keys:
                    vals[check] = -1.0
            if cnt > current_cnt - rollback:
                max_cnt = cnt
                break

            idx = cnt - 1
            log_commit_this(global_m[idx], vals)

        for i in range(max_cnt):
            if i in runs: del runs[i]
    return 

def log_commit():
    global config
    log_commit_at(rollback=0)
    if config.logfile.closed is False:
        config.logfile.close()
    return

def log_build_hdr():
    global config
    global must_have

    interface_lookup = { 'usb0' : 'vz', 'usb1' : 'sp', 'wlan0':'w0',
            'wlan1':'w1', 'eth0' : 'vz',}
    target_lookup = {'127.0.0.1': 'local', '141.212.110.34' : 'bz',
            '141.212.110.236': 'ph', '52.14.177.151':'ec',}
    total_measures = len(args.target_servers) * len(args.interfaces)

    
    config.logfile.write('cnt,ts')
    if config.LOG_OBD:
        config.logfile.write(',mph')
    if config.LOG_GPS:
        config.logfile.write(',lat,lon')
    if config.PWTEST_MODE:
        config.logfile.write(',sleep')

    for target in sorted(config.targets, key=lambda x:
            server_order.index(x)):
        for inf in sorted(config.ifaces, key=lambda x:
                interface_order.index(x)):
            naming = target_lookup[target] + '_' +interface_lookup[inf] 
            config.logfile.write(',' + naming)
    config.logfile.write('\n')
    config.logfile.flush()
    os.fsync(config.logfile.fileno())
    return

def log_print():
    global current_cnt
    global must_have
    global runs
    logrange = 10

    for cnt, vals in runs.iteritems():
        # skip prev values
        if cnt + logrange < current_cnt: continue

        keys = vals.keys()
        for check in must_have:
            if check not in keys:
                vals[check] = -1.0 # not sure this is a good idea...
        mcnt, ts, mph, lat, lon = global_m[cnt - 1]
        print_tmp = ', '.join('{:.3f}'.format(vals[name]) for name in must_have)

        print_hdr = ''
        if config.LOG_OBD:
            print_hdr += '{:.0f},'.format(mph) 
        if config.LOG_GPS:
            print_hdr += '{:10.6f},{:10.6f},'.format(lat, lon)

        if config.PWTEST_MODE:
            print_hdr += '{}, '.format(str(config.INTERVAL))
        print_tmp = print_hdr + print_tmp

        logging.info('%d, %s' % (mcnt, print_tmp))
    return

def log_compute_delta(val):
    start = val['start_ts']
    end = val['end_ts']
    if start is None or end is None:
        return -1.0
    delta = end - start
    return (delta.seconds * 1000.0) + (delta.microseconds / 1000.0)

###############################################################################
# Main Process
###############################################################################
def main(rttqueue):
    global current_cnt, pool, infos
    global terminate, is_terminated
    global logmonitor
    global config

    num_nics = len(args.interfaces)
    num_targets = len(args.target_servers)
    num_runs = config.numruns

    logging.info(str(args.interfaces) + ' ==> ' + \
            str(args.target_servers) + ' x' + str(num_runs))

    if num_runs > 11440:
        logging.warning("cnt_runs " + str(num_runs) + \
                " will probably generate error....")

    logmonitor = Thread(target=log_monitor, args=(rttqueue,),)
    logmonitor.start()

    for target in config.targets:
        for interface in config.ifaces:
            try:
                ipaddr = get_ip_address(interface)
            except Exception as e:
                logging.error('%s' % (str(e)))
                ipaddr = None
                pass

            logging.info('%s, %s, %s' % (interface, ipaddr, target))

            try:
                sck = get_connected(interface, ipaddr, target)
            except Exception as e:
                logging.error('%s' % (str(e)))
                sck = None
                pass

            info = copy.deepcopy(template)
            info['thread_name'] = str(interface) + ',' + target
            info['interface'] = interface
            info['ipaddr'] = ipaddr
            info['target'] = target
            info['socket'] = sck
            info['rttqueue'] = rttqueue
            info['wlan1lock'] = RLock()
            infos.append(info)

    oldlat = .0
    oldlon = .0
    pools = []

    for i in range(num_runs):
        # if (i % 10000) == 0:
        #     newpools = []
        #     tmonitor = Thread(target=thread_monitor, args=(pools,),)
        #     tmonitor.start()
        #     pools = newpools 

        if (i % 60) == 0:
            pool = mpp.ThreadPool(processes=60,)
        current_cnt = i + 1
        __dt = dt.now()
        ts = (__dt).strftime("%s")
        ts = '{}.{}'.format( ts, __dt.microsecond)

        if config.LOG_OBD:
            mph = get_mph(config)
        else:
            mph = -1

        if config.LOG_GPS:
            lat, lon = get_loc(config, oldlat, oldlon)
        else:
            lat, lon = .0, .0

        tmp_tuple = (current_cnt, ts, mph, lat, lon)
        global_m.append(tmp_tuple)

        logging.info('Current cnt :=> %d' % (current_cnt))
        r = pool.map_async(rtt_worker, infos, callback=donedone)
        pools.append(r)

        oldlat = lat
        oldlon = lon
        time.sleep(config.INTERVAL)

    logging.debug('pool waiting...')
    for r in pools:
        r.wait(0.1)
    logging.debug('pool waiting done XD')
    terminate = True

    pool.terminate()
    pool.join()
    logging.debug('pool join done')

    is_terminated = True
    logging.debug('log joining!')
    logmonitor.join()
    logging.debug('log commiting')
    log_commit()
    return


def init(LOG_GPS=True, LOG_OBD=True):
    global config, must_have
    dircheck('log')
    init_logger()
    config = init_config(LOG_GPS, LOG_OBD)
    must_have = ['{:s}-{:s}'.format(intf, tg)
                for intf in interface_order for tg in server_order
                if intf in config.ifaces and tg in config.targets]
    return

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    init(False, False)
    rttqueue = Queue()
    main(rttqueue)
