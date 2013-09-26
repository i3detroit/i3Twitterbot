#!/usr/bin/env python

import urllib2

img = urllib2.urlopen('http://10.13.0.220/cgi-bin/encoder?USER=admin&PWD=123456&SNAPSHOT').read()

with open('twitpic.jpg','wb') as f:
    f.write(img)
