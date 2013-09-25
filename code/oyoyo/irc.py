#!/usr/bin/env python
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from random import choice
import string
import logging

HOST = 'lug.mtu.edu'
PORT = 6667
NICK = 'i3Twitterbot'
CHANS = ['#botsex',]
AUTHD = ['agmlego',]

state = 0

greetings = ['Hello','Hi','Good morning','Good afternoon','Good evening','Hey']

help_msg = {
'status':'Prints out the current state of the space',
'join':'Causes the bot to join a channel',
'part':'Causes the bot to part from a channel',
'op':'Adds a nick to the authorized operators list',
'deop':'Removes a nick from the authorized operators list',
'help':'Provides help on commands',
}

def authed(self,nick,chan):
    isauth = nick in AUTHD
    if not isauth:
        helpers.msg(self.client,chan,'%s: You are not authorized to do that'%nick)
    return isauth


def help_cmd(self,nick,chan,msg):
    if msg == '':
        helpers.msg(self.client,chan,'%s: I can help with %s'%(nick,', '.join(commands.keys())))
    elif msg in commands.keys():
        helpers.msg(self.client,chan,'%s: "%s" -- %s'%(nick,msg,help_msg[msg]))
    else:
        helpers.msg(self.client,chan,'%s: I am a program with limited response capabilities. "%s" is not a command I can help you with. Try asking the right question.'%(nick,msg))

def status(self,nick,chan,msg):
    helpers.msg(self.client,chan,'%s: The space is %s'%(nick,('not responding','OPEN','CLOSED')[state]))

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
'help':help_cmd,
}

def connect_callback(cli):
    helpers.msg(cli, "NickServ", "IDENTIFY blargitty")
    for CHAN in CHANS:
        helpers.join(cli, CHAN)

class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        if NICK in msg:
            n = nick[:nick.find('!')]
            logging.info('%s wants to talk with me!'%n)
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
        logging.info("%s in %s said: %s" % (nick, chan, msg))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli = IRCClient(MyHandler, host=HOST, port=PORT, nick=NICK,
                connect_cb=connect_callback)
    conn = cli.connect()
    while conn.next():
        pass
