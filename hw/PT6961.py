#!/usr/bin/env python

from spi import SPI

port = SPI(2,0)
port.msh = 10000
port.lsbfirst = False
port.mode = 0b11

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

font = {0:0x3f, 1:0x06, 2:0x5b, 3:0x4f, 4:0x66, 5:0x6d, 6:0x7d, 7:0x07, 8:0x7f, 9:0x6f, 'A':0x77, 'B':0x7c, 'C':0x58, 'D':0x5e, 'E':0x79, 'F':0x71, 'G':0x61}

def initDisplay():
	sendCmd(_DISPLAY_6X12)
	sendCmd(_AUTO_INCREMENT)
	initRAM()
	sendCmd(_DISPLAY_14_16)
	print 'Init Display'

def initRAM():
	port.writebytes([0xC0] + [0x00] * 8)
	print 'Init RAM'

def sendCmd(cmd):
	port.writebytes([cmd])
	print 'Sending CMD %s'%cmd

def sendDigit(digit,val):
	port.writebytes([addresses[digit],font[val]])
#	print 'Sending digit %s value %s'%(digit,val)

def sendNum(num,colon=False):
	digits = map(int,str(num))
#	print 'Sending %s as %s (%s)'%(num,digits,('no colon','with colon')[colon])
	sendDigits(digits,colon)

def sendDigits(digits,colon=False):
	digits = [font[d] for d in digits]
	if colon:
		digits[0] |= 0x80
		digits[1] |= 0x80
	d = []
	for addr,digit in zip(addresses,digits):
		d.append(addr)
		d.append(digit)
#	print 'Sending %s as %s'%(digits,d)
	port.writebytes(d)

if __name__ == "__main__":
	freqs = [65000]#reversed(map(lambda x: 12000000/(2**x),xrange(10)))
	msh = freqs[0]
	while True:#for msh in freqs:
		#raw_input()
		port.msh = msh
		print msh
		initDisplay()
		for i in xrange(1000):
			sendNum(i)
