#!/usr/bin/env python
from oyoyo.client import IRCClient
from oyoyo.parse import *
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from random import choice
from ivy.std_api import *
import string
import sys
import logging
from ConfigParser import SafeConfigParser

irclogger = logging.getLogger('IRC')

HOST = None
PORT = None
NICK = None
CHANS = None
TOPIC_CHANS = None
AUTHD = None

state = -1
cli = None

greetings = ['Hello','Hi','Good morning','Good afternoon','Good evening','Hey']

help_msg = {
'status':'Prints out the current state of the space',
'join':'Causes the bot to join a channel',
'part':'Causes the bot to part from a channel',
'op':'Adds a nick to the authorized operators list',
'deop':'Removes a nick from the authorized operators list',
'die':'Kills the bot',
'help':'Provides help on commands',
}

def state_text(state):
    return ('not responding','CLOSED','OPEN')[state+1]

def authed(self,nick,chan):
    isauth = nick in AUTHD
    if not isauth:
        helpers.msg(self.client,chan,'%s: You are not authorized to do that'%nick)
    return isauth

def die(self,nick,chan,msg):
    global cli
    if authed(self,nick,chan):
        IvyStop()
        sys.exit()

def help_cmd(self,nick,chan,msg):
    if msg == '':
        helpers.msg(self.client,chan,'%s: I can help with %s'%(nick,', '.join(commands.keys())))
    elif msg in commands.keys():
        helpers.msg(self.client,chan,'%s: "%s" -- %s'%(nick,msg,help_msg[msg]))
    else:
        helpers.msg(self.client,chan,'%s: I am a program with limited response capabilities. "%s" is not a command I can help you with. Try asking the right question.'%(nick,msg))

def status(self,nick,chan,msg):
    helpers.msg(self.client,chan,'%s: The space is %s'%(nick,state_text(state)))

def add_op(self,nick,chan,msg):
    if authed(self,nick,chan):
        if msg not in AUTHD:
            AUTHD.append(msg)
            helpers.msg(self.client,chan,'%s: OK, I added %s as a bot operator'%(nick,msg))
        elif msg == nick:
            helpers.msg(self.client,chan,'%s: Um...you already are an operator...'%(nick))
        else:
            helpers.msg(self.client,chan,'%s: Um...%s is *already* a bot operator...'%(nick,msg))
        

def del_op(self,nick,chan,msg):
    if authed(self,nick,chan):
        if msg in AUTHD:
            AUTHD.remove(msg)
            helpers.msg(self.client,chan,'%s: OK, I removed %s as a bot operator'%(nick,msg))
        else:
            helpers.msg(self.client,chan,'%s: Um...%s is not a bot operator...'%(nick,msg))

def join(self,nick,chan,msg):
    if authed(self,nick,chan):
        if msg not in CHANS:
            CHANS.append(msg)
            helpers.join(cli, msg)
            helpers.msg(self.client,chan,'%s: OK, I joined %s'%(nick,msg))
        elif msg == chan:
            helpers.msg(self.client,chan,'%s: Um...this *is* %s...'%(nick,msg))
        else:
            helpers.msg(self.client,chan,'%s: Um...I am *already* in %s...'%(nick,msg))

def part(self,nick,chan,msg):
    if authed(self,nick,chan):
        if msg in CHANS:
            CHANS.remove(msg)
            helpers.part(cli, msg)
            helpers.msg(self.client,chan,'%s: OK, I parted %s'%(nick,msg))
        else:
            helpers.msg(self.client,chan,'%s: Um...I am not in %s...'%(nick,msg))

commands = {
'status':status,
'join':join,
'part':part,
'op':add_op,
'deop':del_op,
'die':die,
'help':help_cmd,
}

def status_change(agent, status):
    global state
    global cli
    status = int(status)
    ns = state_text(status)
    os = state_text(state)
    for chan in TOPIC_CHANS:
        helpers.msg(cli,chan,'The space is now %s'%ns)
    irclogger.info('Space went from %s to %s, according to %r'%(os,ns,agent))
    state = status

def connect_callback(cli):
    helpers.identify(cli,"blargitty")
    helpers.user(cli,NICK,'i3Detroit Twitterbot Space-status Bot')
    for CHAN in CHANS:
        helpers.join(cli, CHAN)

def oncxproc(agent, connected):
    if connected == IvyApplicationDisconnected :
        irclogger.warning('Ivy application %r was disconnected', agent)
    else:
        irclogger.info('Ivy application %r was connected', agent)
    irclogger.debug('Current Ivy applications are [%s]', IvyGetApplicationList())

def ondieproc(agent, id):
    irclogger.warning('Received the order to die from %r with id = %d', agent, id)

class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        if NICK in msg:
            n = nick[:nick.find('!')]
            irclogger.info('%s wants to talk with me!'%n)
            cmd = msg.replace(NICK,'').replace(':','').strip()
            idx = cmd.find(' ')
            if idx != -1:
                arg = cmd[cmd.find(' ')+1:]
                idx = cmd[:cmd.find(' ')]
            else:
                idx = cmd
                arg = ''
            if idx.lower() in commands.keys():
                commands[idx.lower()](self,n,chan,arg)
            elif ''.join([c for c in cmd if c in string.letters+' ']) in greetings:
                helpers.msg(self.client,chan,'%s: %s!'%(n,choice(greetings)))
            elif cmd.startswith('help'):
                help_cmd(self,n,chan,cmd.replace('help','').strip())
            else:
                helpers.msg(self.client,chan,'%s: "%s" is not a command I recognize. I can respond cordially to greetings, or to any of these commands: %s'%(n,cmd,', '.join(commands.keys())))
        irclogger.info("%s in %s said: %s" % (nick, chan, msg))

if __name__ == "__main__":
    IvyInit('i3Twitterbot_IRC','[i3Twitterbot_IRC is ready]',0,oncxproc,ondieproc)
    IvyStart('127.255.255.255:2010')
    IvyBindMsg(status_change,'^status=(-?[0-1])')
    irclogger.basicConfig(level=logging.INFO)

    config = SafeConfigParser({'access_key':None,'access_secret':None})
    config.read('twitterbot.ini')
   
    HOST = config.get('IRC','server')
    PORT = config.get('IRC','port')
    NICK = config.get('IRC','nick')
    CHANS = config.get('IRC','channels').split(',')
    TOPIC_CHANS = config.get('IRC','announce').split(',')
    AUTHD = config.get('IRC','authed_users').split(',')

    cli = IRCClient(MyHandler, host=HOST, port=PORT, nick=NICK,
                connect_cb=connect_callback)
    conn = cli.connect()
    while True:
        conn.next()
