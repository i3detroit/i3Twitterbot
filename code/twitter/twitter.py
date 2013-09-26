#!/usr/bin/env python
import sys
import tweepy
from ivy.std_api import *
from ConfigParser import SafeConfigParser
import logging

twlogger = logging.getLogger('Twitter')

state = -1

api = None

def state_text(state):
    return ('not responding','CLOSED','OPEN')[state+1]

def status_change(agent, status):
    global state
    global api
    status = int(status)
    ns = state_text(status)
    os = state_text(state)
    api.update_status('The space is now %s'%ns)
    twlogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))
    state = status

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        twlogger.warning('Ivy application %r was disconnected', agent)
    else:
        twlogger.info('Ivy application %r was connected', agent)
    twlogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    twlogger.warning('Received the order to die from %r with id = %d', agent, id)

if __name__ == "__main__":
    config = SafeConfigParser({'access_key':None,'access_secret':None})
    config.read('twitterbot.ini')
    
    consumer_key = config.get('Twitter','consumer_key')
    consumer_secret = config.get('Twitter','consumer_secret')
    access_key = config.get('Twitter','access_key')
    access_secret = config.get('Twitter','access_secret')
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    if not access_key or not access_secret:
        # OAuth dance
        try:
            redirect_url = auth.get_authorization_url()
            print 'Go here to get the OAuth PIN! %s'%redirect_url
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'
            sys.exit(1)
        
        verifier = raw_input('Verifier: ')
        auth.get_access_token(verifier)
        config.set('Twitter','access_key',auth.access_token.key)
        config.set('Twitter','access_secret',auth.access_token.secret)
    else:
        auth.set_access_token(access_key,access_secret)
    
    api = tweepy.API(auth)
    
    IvyInit('i3Twitterbot_TW','[i3Twitterbot_TW is ready]',0,oncxproc,ondieproc)
    IvyStart('127.255.255.255:2010')
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    twlogger.basicConfig(level=logging.INFO)
    IvyMainLoop()
