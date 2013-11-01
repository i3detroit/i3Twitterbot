#!/usr/bin/env python
# GPIO2_6 is green (open) LED, active low
# GPIO2_7 is red (closed) LED, active low
# GPIO2_9 is switch, low for open
from bbio import *
from ivy.std_api import *
import logging
import time
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser

hwlogger = logging.getLogger('HW_IRQ')

GREEN_LED = GPIO2_6
RED_LED = GPIO2_7
SWITCH = GPIO2_9
DEBOUNCE = 200

interested = None

state = -1

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        hwlogger.warning('Ivy application %r was disconnected', agent)
    else:
        name = agent[agent.find('(')+1:agent.find(')')]
        hwlogger.info('Ivy application %r was connected', agent)
        if name in interested:
            IvySendMsg('status=%1d'%state)
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
    if led_change.oldstate != state and (datetime.now() - led_change.oldtime) > timedelta(milliseconds=DEBOUNCE):
        hwlogger.info('The space is %s'%('OPEN','CLOSED')[state])
        digitalWrite(GREEN_LED, state)
        digitalWrite(RED_LED, not state)
        led_change.oldstate = state
        led_change.oldtime = datetime.now()

def setup():
    pinMode(GREEN_LED, OUTPUT)
    pinMode(RED_LED, OUTPUT)
    pinMode(SWITCH, INPUT)
    attachInterrupt(SWITCH,led_change,BOTH)

def loop():
    time.sleep(1.0)

if __name__ == "__main__":
    config = SafeConfigParser()
    config.read('twitterbot.ini')
   
    ivy_name = config.get('Hardware','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_req,'^status\?')
    hwlogger.setLevel(level=getattr(logging,config.get('Hardware','log_level')))
    DEBOUNCE = config.get('Hardware','debounce')
    interested = []
    for client in config.get('Hardware','interested').split(','):
        interested.append(config.get(client,'ivy_name'))
    run(setup, loop)
