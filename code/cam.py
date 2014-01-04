#!/usr/bin/env python

import urllib2
from time import sleep
from datetime import datetime,timedelta
from ivy.std_api import *
from ConfigParser import SafeConfigParser
import logging
import logging.config
import PT6961 as led

logging.config.fileConfig('conf/twitterbot.log.ini')
camlogger = logging.getLogger('Twitterbot.camera')

CAMURL = None
CAMTIME = None
state = -1

def state_text(state):
    return ('not responding','CLOSED','OPEN')[state+1]

def status_change(agent, status):
    global state
    status = int(status)
    ns = state_text(status)
    os = state_text(state)
    if status == 1:
        # countdown
        start = datetime.now()
        now = datetime.now()
        delta = timedelta(seconds=CAMTIME)
        camlogger.info('Starting countdown of %d seconds!'%CAMTIME)
        diff = now - start
        while diff < delta:
            led.sendNum((CAMTIME-1-diff.seconds)*100+99-(diff.microseconds/10000),high_dot=True)
            sleep(0.01)
            now = datetime.now()
            diff = now - start
    
        img = urllib2.urlopen(CAMURL).read()
        camlogger.info('Camera image saved!')
        with open('twitpic.jpg','wb') as f:
            f.write(img)
            IvySendMsg('newpic')
    camlogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))
    state = status

def heartbeat(agent):
    IvySendMsg('hb_ack')

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        camlogger.warning('Ivy application %r was disconnected', agent)
    else:
        camlogger.info('Ivy application %r was connected', agent)
    camlogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    camlogger.warning('Received the order to die from %r with id = %d', agent, id)

if __name__ == "__main__":
    config = SafeConfigParser()
    config.read('conf/twitterbot.ini')

    camlogger.setLevel(level=getattr(logging,config.get('Camera','log_level')))
    CAMURL = config.get('Camera','camurl')
    CAMTIME = int(config.get('Camera','countdown'))

    ivy_name = config.get('Camera','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    IvyBindMsg(heartbeat,'^hb_syn')
    IvySendMsg('status?')

    led.port.msh = 12000000
    led.initDisplay()
    while True:
        t = datetime.now()
        if t.second%10 < 5:
            # show time
            #print 'Time %02d:%02d:%02d'%(t.hour,t.minute,t.second)
            led.sendNum(t.hour*100+t.minute,low_dot=True,high_dot=True)
        else:
            # show date
            #print 'Date %04d-%02d-%02d'%(t.year,t.month,t.day)
            led.sendNum(t.month*100+t.day,low_dot=True,high_dot=False)
        sleep(1)
