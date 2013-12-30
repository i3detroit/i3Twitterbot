#!/usr/bin/env python

import urllib2
from ivy.std_api import *
from ConfigParser import SafeConfigParser
import logging

logging.basicConfig()
camlogger = logging.getLogger('Camera')

CAMURL = None
state = -1

def state_text(state):
    return ('not responding','CLOSED','OPEN')[state+1]

def status_change(agent, status):
    global state
    status = int(status)
    ns = state_text(status)
    os = state_text(state)
    img = urllib2.urlopen(CAMURL).read()
    with open('twitpic.jpg','wb') as f:
        f.write(img)
        IvySendMsg('newpic')
    camlogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))
    state = status

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
    config.read('twitterbot.ini')

    camlogger.setLevel(level=getattr(logging,config.get('Camera','log_level')))
    CAMURL = config.get('Camera','camurl')

    ivy_name = config.get('Camera','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    IvyMainLoop()
