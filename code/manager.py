#!/usr/bin/env python

from ivy.std_api import *
import logging
import logging.config
from ConfigParser import SafeConfigParser
import os
import sys
import subprocess
import signal
from datetime import datetime,timedelta
from time import sleep

logging.config.fileConfig('conf/twitterbot.log.ini')
mainlogger = logging.getLogger('Twitterbot.manager')

agents = {}

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        mainlogger.warning('Ivy application %r was disconnected', agent)
    else:
        name = agent.agent_name#agent['agent_name'][agent['agent_name'].find('(')+1:agent['agent_name'].find(')')]
        mainlogger.info('Ivy application %r was connected', agent)
    mainlogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    mainlogger.warning('Received the order to die from %r with id = %d', agent, id)

def heartbeat(agent):
    global agents
    if agent in agents:
        agents[agent]['lasthb'] = datetime.now()
        mainlogger.info('Got heartbeat from %s'%agent)
    else:
        mainlogger.warn('Agent %s not in agents...'%agent)
        agents[agent] = {'pid':None,'sp':None,'lasthb':datetime.now()}

def startAgent(agent):
    global agents
    proc = config.get(agent,'proc')
    if agent not in agents:
        agents[agent] = {'pid':None,'sp':None,'lasthb':datetime.now()}

    agents[agent]['sp'] = subprocess.Popen('python %s &'%proc,shell=True)
    agents[agent]['pid'] = agents[agent]['sp'].pid + 1 #shell=True means pid is the shell, so +1 is the agent
    agents[agent]['lasthb'] = datetime.now()
    agents[agent]['ivy_name'] = config.get(agent,'ivy_name')

if __name__ == "__main__":
    config = SafeConfigParser()
    config.read('conf/twitterbot.ini')

    if 'access_key' not in config.options('Twitter'):
        mainlogger.critical('Twitter client needs OAuth dance. Please run it manually, then rerun this script.')
        sys.exit(1)

   
    ivy_name = config.get('Manager','ivy_name')
    IvyInit(ivy_name,'[%s is ready]'%ivy_name,0,oncxproc,ondieproc)
    IvyStart(config.get('General','ivy_bus'))
    IvyBindMsg(heartbeat,'^hb_ack')
    mainlogger.setLevel(level=getattr(logging,config.get('Manager','log_level')))

    timeout = timedelta(seconds=int(config.get('Manager','timeout')))
    interested = config.get('Manager','agents').split(',')

    for agent in interested:
        startAgent(agent)

    while True:
        for agent in agents:
            if datetime.now() - agents[agent]['lasthb'] > timeout:
                IvySendDieMsg(IvyGetApplication(agents[agent]['ivy_name']))
                try:
                    os.kill(agents[agent]['pid'],signal.SIGKILL)
                except OSError,e:
                    if e[0] != 3:
                        raise e
                startAgent(agent)
                mainlogger.warn('Agent %s died and was reborn.'%agent)
            else:
                IvySendMsg('hb_syn')
        sleep(1)
