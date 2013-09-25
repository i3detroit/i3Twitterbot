#!/usr/bin/env python
# GPIO2_6 is green (open) LED, active low
# GPIO2_7 is red (closed) LED, active low
# GPIO2_9 is switch, low for open
from bbio import *
from ivy.std_api import *
import logging
import time
from datetime import datetime, timedelta

GREEN_LED = GPIO2_6
RED_LED = GPIO2_7
SWITCH = GPIO2_9

state = -1

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        logging.warning('Ivy application %r was disconnected', agent)
    else:
        logging.info('Ivy application %r was connected', agent)
        if '_IRC' in agent or '_TW' in agent:
            IvySendMsg('status=%1d'%state)
    logging.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    logging.warning('Received the order to die from %r with id = %d', agent, id)

def status_req(agent):
    logging.info('%s requested status.'%agent)
    IvySendMsg('status=%1d'%state)

def led_change():
    global state
    if not hasattr(led_change,'oldstate'):
        led_change.oldstate = -1
        led_change.oldtime = datetime.min
    state = digitalRead(SWITCH)
    if led_change.oldstate != state and (datetime.now() - led_change.oldtime) > timedelta(milliseconds=200):
        logging.info('The space is %s'%('OPEN','CLOSED')[state])
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
    IvyInit('i3Twitterbot_HW','[i3Twitterbot_HW is ready]',0,oncxproc,ondieproc)
    IvyStart('127.255.255.255:2010')
    IvyBindMsg(status_req,'^status\?')
    logging.basicConfig(level=logging.INFO)
    run(setup, loop)
