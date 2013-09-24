#!/usr/bin/env python

from spi import SPI
from time import sleep
from datetime import datetime

port = SPI(2,0)
port.msh = 100000
#port.lsbfirst = True
port.mode = 0b00

_DISPLAY_6X12 = 0x02                         
_DISPLAY_7X11 = 0x03                         
_AUTO_INCREMENT = 0x40                       
_FIXED_ADDRESS = 0x44
_DISPLAY_OFF = 0x80
_DISPLAY_1_16 = 0x88                         
_DISPLAY_2_16 = 0x89                         
_DISPLAY_4_16 = 0x8A                         
_DISPLAY_10_16 = 0x8B                        
_DISPLAY_11_16 = 0x8C                        
_DISPLAY_12_16 = 0x8D                        
_DISPLAY_13_16 = 0x8E                        
_DISPLAY_14_16 = 0x8F

addresses = (0xC0,0xC2,0xC4,0xC6)

font = {	0:  0xFC,
		1:  0x60,
		2:  0xDA,
		3:  0xF2,
		4:  0x66,
		5:  0xB6,
		6:  0xBE,
		7:  0xE0,
		8:  0xFE,
		9:  0xF6,
		'A':0xEE,
		'B':0x3E,
		'C':0x9C,
		'D':0x7A,
		'E':0x9E,
		'F':0x8E
	}

def fixEndian(b):
	fbyte = int('{:08b}'.format(b)[::-1],2)
	#print 'Flipped: %02X -> %02X'%(b,fbyte)
	return fbyte

def initDisplay():
	sendCmd(_DISPLAY_6X12)
	sendCmd(_AUTO_INCREMENT)
	initRAM()
	sendCmd(_DISPLAY_14_16)
	print 'Init Display'

def initRAM():
	port.writebytes([fixEndian(0xC0)] + [0x00] * 8)
	print 'Init RAM'

def sendCmd(cmd):
	port.writebytes([fixEndian(cmd)])
	print 'Sending CMD %s'%cmd

def sendCmds(*cmds):
	port.writebytes(map(fixEndian,cmds))
	print 'Sending CMDs %s'%str(cmds)

def sendDigit(digit,val):
	port.writebytes([fixEndian(addresses[digit]),font[val]])
	print 'Sending digit %s value %s'%(digit,val)

def sendNum(num,colon=False):
	digits = map(int,'%04d'%num)
	print 'Sending %s as %s (%s)'%(num,digits,('no colon','with colon')[colon])
	sendDigits(digits,colon)

def sendDigits(digits,colon=False):
	digits = [font[d] for d in digits]
	if colon:
		digits[0] |= 0x1
		digits[1] |= 0x1
	d = []
	for addr,digit in zip(addresses,digits):
		d.append(fixEndian(addr))
		d.append(digit)
	print 'Sending %s as %s'%(digits,d)
	port.writebytes(d)

if __name__ == "__main__":
	port.msh = 12000000
	initDisplay()
	while True:
		t = datetime.now()
		print t
		sendNum(t.hour*100+t.minute,t.second%2)
		sleep(1)
