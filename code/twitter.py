#!/usr/bin/env python
import sys
import tweepy
from datetime import datetime
from ivy.std_api import *
from ConfigParser import SafeConfigParser
import logging
import logging.config
import sys

logging.config.fileConfig('conf/twitterbot.log.ini')
twlogger = logging.getLogger('Twitterbot.Twitter')

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
    if ns == 'OPEN':
        twlogger.info('Space is opened, waiting for picture')
    else:
        api.update_status(status='At %s, the space is now %s'%(datetime.now(),ns))
    twlogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))
    state = status

def picture_change(agent):
    global state
    global api
    ns = state_text(status)
    if state == 1:
        api.update_with_media('twitpic.jpg',status='At %s, the space is now %s'%(datetime.now(),ns))
        twlogger.info('Got new image from %s, posting.'%agent)

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        twlogger.warning('Ivy application %r was disconnected', agent)
    else:
        twlogger.info('Ivy application %r was connected', agent)
    twlogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    twlogger.warning('Received the order to die from %r with id = %d', agent, id)

def heartbeat(agent):
    IvySendMsg('hb_ack')

if __name__ == "__main__":
    config = SafeConfigParser({'access_key':None,'access_secret':None})
    config.read('conf/twitterbot.ini')
    
    twlogger.setLevel(level=getattr(logging,config.get('Twitter','log_level')))
   
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
            twlogger.error('Error! Failed to get request token.')
            sys.exit(1)
        
        verifier = raw_input('Verifier: ')
        auth.get_access_token(verifier)
        config.set('Twitter','access_key',auth.access_token.key)
        config.set('Twitter','access_secret',auth.access_token.secret)
        config.write(open('conf/twitterbot.ini','w'))
        sys.exit(0)
    else:
        auth.set_access_token(access_key,access_secret)
    
    api = tweepy.API(auth)
    
    ivy_name = config.get('Twitter','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    IvyBindMsg(picture_change,'^newpic')
    IvyBindMsg(heartbeat,'^hb_syn')
    IvyMainLoop()
