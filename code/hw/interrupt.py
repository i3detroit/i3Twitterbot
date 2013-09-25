#!/usr/bin/env python
# GPIO2_6 is green (open) LED, active low
# GPIO2_7 is red (closed) LED, active low
# GPIO2_9 is switch, low for open
from bbio import *
import time
from datetime import datetime, timedelta

GREEN_LED = GPIO2_6
RED_LED = GPIO2_7
SWITCH = GPIO2_9

def led_change():
  if not hasattr(led_change,'oldstate'):
    led_change.oldstate = -1
    led_change.oldtime = datetime.min
  state = digitalRead(SWITCH)
  if led_change.oldstate != state and (datetime.now() - led_change.oldtime) > timedelta(milliseconds=200):
    print 'The space is %s'%('OPEN','CLOSED')[state]
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

run(setup, loop)