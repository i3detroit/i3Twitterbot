#!/usr/bin/env python

from ivy.std_api import *
import string
import sys
from os.path import join
import logging
from ConfigParser import SafeConfigParser
import paramiko
import sys
import traceback
logging.basicConfig()
weblogger = logging.getLogger('WEB')

username = None
password = None
hostname = None
port = None
filepath = None
filename = None

def state_text(state):
    return ('not responding','CLOSED','OPEN')[state+1]

def status_change(agent, status):
    global state

    status = int(status)
    ns = state_text(status)
    os = state_text(state)
    weblogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))   
    state = status
   
    try:
        t = paramiko.Transport((hostname, port))                                    
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        dirlist = sftp.listdir(filepath)
    
        if filename not in dirlist:
            weblogger.warn('File %s does not exist on server; will'
                           ' create.'%filename)
    
        sftp.open(join(filepath,filename), 'w').write(('closed','open')[state])
    except Exception, e:
        weblogger.error('Exception %s'%e)

def picture_change(agent, status):
    try:
        t = paramiko.Transport((hostname, port))                                    
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put('twitpic.jpg',join(filepath,'twitpic.jpg'))
    except Exception, e:
        weblogger.error('Exception %s'%e)

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        weblogger.warning('Ivy application %r was disconnected', agent)
    else:
        weblogger.info('Ivy application %r was connected', agent)
    weblogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    weblogger.warning('Received the order to die from %r with id = %d', agent, id)


if __name__ == "__main__":
    config = SafeConfigParser()
    config.read('twitterbot.ini')

    weblogger.setLevel(level=getattr(logging,config.get('Website','log_level')))

    username = config.get('Website','username')
    password = config.get('Website','password')
    port = int(config.get('Website','port'))
    hostname = config.get('Website','hostname')
    filepath = config.get('Website','filepath')
    filename = config.get('Website','filename')

    ivy_name = config.get('Website','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    IvyBindMsg(picture_change,'^newpic')
    IvyMainLoop()
