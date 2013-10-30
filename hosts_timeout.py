#!/usr/bin/python

import sys
from time import sleep, time
import argparse
import collections

HOSTS = '/etc/hosts'
#HOSTS = 'hosts'

def read_hosts():
    return open(HOSTS, 'r').readlines()


def write_hosts(lines):
    f = open(HOSTS, 'w')
    for line in lines:
        f.write(line)
    f.close()

def toggle(lines, domain):
    newlines = []
    found = False

    for line in lines:
        if '\t' not in line:
            newlines.append(line)
            continue
            
        ip, domains = line.split('\t')
        if domain in domains:
            found = True
            if ip[0]=='#':
                newlines.append( line[1:] )
            else:
                newlines.append( '#' + line )
        else:
            newlines.append(line)

    if found:
        return newlines
    else:
        return None

def today():
    return "today"

def clock_in(lines, hostname, elapsed):
    if lines[-1][0] == '#':
        date, data = lines[-1][1:].split('|')
        date = date.strip()
        data = collections.defaultdict(float, eval(data))
        if date!=today():
            report(data, True)
            date = today()
            data = collections.defaultdict(float)                    
        insert = False
    else:
        date = today()
        data = collections.defaultdict(float)
        insert = True
    
    
    data[hostname] += elapsed
    
    line = '# %s | %s'%(date, str(dict(data)))
    report(data)
    if insert:
        lines.append(line)
    else:
        lines[-1] = line
    return lines
    
def report(data, yesterday=False):
    if yesterday:
        s = "Yesterday's Report"
    else:
        s = "Today's Report"
        
    print '===== %17s ====='%s 
    
    for host, t in sorted(data.items(), key=lambda a: a[1], reverse=True):
        s = int(t)%60
        m = int(t/60)%60
        h = int(t/3600)
        print "%-20s %02d:%02d:%02d"%(host, h, m, s)
    

parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('minutes', default=5, type=int, nargs="?")
parser.add_argument('--toggle', action='store_true')
args = parser.parse_args()

seconds = args.minutes * 60

print "Initiating Change" 
lines = read_hosts()
lines = toggle(lines, args.hostname)
if lines is None:
    print "Can't find %s!"%args.hostname
    exit(0)
write_hosts(lines)

if args.toggle:
    exit(0)              

print "Sleeping"
start = time()
try:
    sleep(seconds)
except:
    None

elapsed = time() - start

print "Reverting"
lines = toggle(lines, args.hostname)

lines = clock_in(lines, args.hostname, elapsed)

write_hosts(lines)

