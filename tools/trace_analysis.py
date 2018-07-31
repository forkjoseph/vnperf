#!/usr/bin/env python
# USAGE: ./trace_analysis.py -f [TRACE(s)]

import argparse
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description='Vehicular network trace analyzer')
parser.add_argument('-f', '--filenames', help='', default=[],
        required=True, type=str, action='append')
args = parser.parse_args()

naming = {'vz' : 'Verizon', 'sp' : 'Sprint', 'w1': 'XFinityWiFi'}

def load(filename):
    return pd.read_csv(filename)

def print_stat(df):
    columns = [x for x in df.columns.values if '_' in x]
    hdr = ['name', 'min', 'max', 'median', 'mean', 'std']
    hdr2 = [5, 95]
    print '\t|',
    for h in hdr: 
        print'{: ^9s}|'.format(h),
    for h in hdr2:
        print'{: ^9s}|'.format(str(h)),
    print ''

    for c in columns:
        # tmp = (df[c].apply(lambda x: float('NaN') if x < 0 else x)).tolist()
        tmp = (df[c].apply(lambda x: float('inf') if x < 0 else x)).tolist()
        print '\t|{: ^10.10s}|'.format(naming[c.split('_')[1]]),
        for h in hdr[1:]: 
            try:
                print '{: ^9.2f}|'.format(getattr(np, 'nan'+h)(tmp)),
            except AttributeError:
                print '{: ^9.2f}|'.format(getattr(np, h)(tmp)),
        for h in hdr2:
            print '{: ^9.2f}|'.format(np.percentile(tmp, h)), 
        print ''

    tmp = (df['mph'].apply(lambda x: float('NaN') if x < 0 else x)).tolist()
    print '\t|{: ^10.10s}|'.format('MPH'),
    for h in hdr[1:]: print '{: ^9.2f}|'.format(getattr(np, 'nan'+h)(tmp)),
    print ''
    mphs = df['mph'].tolist()
    print 'MPH', round(np.mean(mphs),2), 'cnt', len(mphs)
    print 'Duration', round(float(len(mphs))/60.0, 1), 'mins'
    # print 'Total of {:d} interfaces: '.format(len(measures)),
    # for k, v in measures: print '{:s} ({:d}),'.format(k, len(v)),
    # print '\n'
    return


def main():
    for f in args.filenames:
        df = load(f)
        print_stat(df)
    return

if __name__ == '__main__':
    main()
