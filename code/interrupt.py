#!/usr/bin/env python
# GPIO2_6 is green (open) LED, active low
# GPIO2_7 is red (closed) LED, active low
# GPIO0_9 is switch, low for open
from bbio import *
from ivy.std_api import *
import logging
import logging.config
import time
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser
from termcolor import cprint

logging.config.fileConfig('conf/twitterbot.log.ini')
hwlogger = logging.getLogger('Twitterbot.hardware')

GREEN_LED = GPIO2_6
RED_LED = GPIO2_7
SWITCH = GPIO0_7
DEBOUNCE = 200
DWELL = 2000

interested = None

state = -1

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        hwlogger.warning('Ivy application %r was disconnected', agent)
    else:
        name = agent.agent_name
        hwlogger.info('Ivy application %r was connected (name=%s)'%(agent,name))
        if name in interested and state != -1:
            IvySendMsg('status=%1d'%state)
            hwlogger.info('%r is interested in updates.'%agent)
    hwlogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    hwlogger.warning('Received the order to die from %r with id = %d', agent, id)

def status_req(agent):
    hwlogger.info('%s requested status.'%agent)
    IvySendMsg('status=%1d'%state)

def led_change():
    global state
    if not hasattr(led_change,'oldstate'):
        led_change.oldstate = -1
        led_change.oldtime = datetime.min
    state = digitalRead(SWITCH)
    if led_change.oldstate != state:
        if(datetime.now() - led_change.oldtime) > timedelta(milliseconds=DEBOUNCE):
            if(datetime.now() - led_change.oldtime) < timedelta(milliseconds=DWELL):
                hwlogger.info('Rate-limiting...')
            else:
                hwlogger.info('The space is %s'%('OPEN','CLOSED')[state])
                digitalWrite(GREEN_LED, state)
                digitalWrite(RED_LED, not state)
                led_change.oldstate = state
                led_change.oldtime = datetime.now()
                IvySendMsg('status=%1d'%(1-state))

def heartbeat(agent):
    IvySendMsg('hb_ack')

def setup():
    pinMode(GREEN_LED, OUTPUT)
    pinMode(RED_LED, OUTPUT)
    pinMode(SWITCH, INPUT)
    attachInterrupt(SWITCH,led_change,BOTH)
    state = digitalRead(SWITCH)
    led_change()

def loop():
    time.sleep(1.0)

if __name__ == "__main__":
    config = SafeConfigParser()
    config.read('conf/twitterbot.ini')
   
    ivy_name = config.get('Hardware','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_req,'^status\?')
    IvyBindMsg(heartbeat,'^hb_syn')
    hwlogger.setLevel(level=getattr(logging,config.get('Hardware','log_level')))
    DEBOUNCE = int(config.get('Hardware','debounce'))
    DWELL = int(config.get('Hardware','dwell'))
    interested = []
    for client in config.get('Hardware','interested').split(','):
        interested.append(config.get(client,'ivy_name'))
    print interested
    run(setup, loop)
