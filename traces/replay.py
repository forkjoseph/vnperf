#!/usr/bin/env python2.7
""" replay mobile network traces in testbed """ 

__author__ = "HyunJong (Joseph) Lee"
__email__ = "hyunjong at umich dot edu"
__license__ = "Apache License v2"

import subprocess
import signal
import sys
import time
import pandas as pd 

gStop = False
supported = ['verizon', 'sprint', 'xfinitywifi']

def help():
    print 'usage: ./replay.py [NAME OF TRACE]'
    sys.exit(0)

def signal_handler(signal, frame):
    global gStop
    print ('You pressed Ctrl+C!')
    gStop = True
    init_latency()
    print ('gracefully terminated...!')
    sys.exit(0)

#========================= REPLAYER ===============================
def change(rtts):
    rtt1 = '50000'
    rtt2 = '50000'
    rtt3 = '50000'
    loss1 = ''
    loss2 = ''
    loss3 = ''

    if len(rtts) > 2:
        rtt3 = rtts[2]
    if len(rtts) > 1:
        rtt2 = rtts[1]
    if len(rtts) > 0:
        rtt1 = rtts[0]

    if int(rtt3) <= 0.0:
        print '[net-3 loss]'
        rtt3 = '1'
        loss3 = '100.0'

    if int(rtt2) <= 0.0:
        print '[net-2 loss]'
        rtt2 = '1'
        loss2 = '100.0'

    if int(rtt1) <= 0.0:
        print '[net-1 loss]'
        rtt1 = '1'
        loss1 = '100.0'

    cmd = ['./change.sh', rtt1, rtt2, rtt3]
    cmd += [loss1, loss2, loss3]
    rc = subprocess.check_call(cmd)
    return rtt1, rtt2, rtt3


def load_traces(filename, timeout=3000):
    global gStop

    df = pd.read_csv(filename)
    col = [x for x in df.columns.values if x in supported]

    dropping = []
    for column in df:
        if not column in col:
            dropping.append(column)

    for d in dropping: 
        df = df.drop(d, 1)

    for c in col:
        df[c] = df[c].divide(2.0)   # RTT to one-way delay
        df[c] = df[c].round()       # to int
        df[c] = df[c].astype(int)

    for c in col: df[c] = df[c].astype(str) 
    
    print (df.describe(include='all'))
    return df

def replay_traces(df):
    global gStop

# starting index
    minidx = 0
    maxidx = 3600
    maxidx += minidx
    cnt = 0
    for idx, row in df.iterrows():
        if idx < minidx: continue
        if idx > maxidx: break
        if gStop: break

        rtts = row.tolist()
        print (str(cnt) + '>> ' +  'ms, '.join(rtts) + 'ms')
        change(rtts)

        time.sleep(1.0)
        cnt += 1

    return

def init_latency():
    latency = ['1', '1', '1']
    change(latency)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) < 2:
        help()

    filename = sys.argv[1]
    init_latency()

    df = load_traces(filename)
    replay_traces(df)
    init_latency()
