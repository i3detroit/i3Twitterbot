#!/usr/bin/env python
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from random import choice
import logging

HOST = 'lug.mtu.edu'
PORT = 6667
NICK = 'i3Twitterbot'
CHAN = '#botsex'

state = 0

greetings = ['Hello','Hi','Good morning','Good afternoon','Good evening','Hey']

help_msg = {
'status':'Prints out the current state of the space',
'help':'Provides help on commands',
}

def help_cmd(self,nick,msg):
    if msg == '':
        helpers.msg(self.client,CHAN,'%s: I can help with %s'%(nick,', '.join(commands.keys())))
    elif msg in commands.keys():
        helpers.msg(self.client,CHAN,'%s: "%s" -- %s'%(nick,msg,help_msg[msg]))
    else:
        helpers.msg(self.client,CHAN,'%s: I am a program with limited response capabilities. "%s" is not a command I can help you with. Try asking the right question.'%(nick,msg))

def status(self,nick,msg):
    helpers.msg(self.client,CHAN,'%s: The space is %s'%(nick,('not responding','OPEN','CLOSED')[state]))

commands = {
'status':status,
'help':help_cmd,
}

def connect_callback(cli):
    helpers.msg(cli, "NickServ", "IDENTIFY blargitty")
    helpers.join(cli, CHAN)

class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        if NICK in msg:
            n = nick[:nick.find('!')]
            logging.info('%s wants to talk with me!'%n)
            cmd = msg.replace(NICK,'').replace(':','').strip()
            if cmd in commands:
                commands[cmd](self,n,cmd)
            elif cmd in greetings:
                helpers.msg(self.client,CHAN,'%s: %s!'%(n,choice(greetings)))
            elif cmd.startswith('help'):
                help_cmd(self,n,cmd.replace('help','').strip())
            else:
                helpers.msg(self.client,CHAN,'%s: "%s" is not a command I recognize. I can respond cordially to greetings, or to any of these commands: %s'%(n,cmd,', '.join(commands.keys())))
        logging.info("%s in %s said: %s" % (nick, chan, msg))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli = IRCClient(MyHandler, host=HOST, port=PORT, nick=NICK,
                connect_cb=connect_callback)
    conn = cli.connect()
    while conn.next():
        pass
