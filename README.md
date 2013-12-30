i3Twitterbot
============

Twitterbot!

Features
========
* Near-realtime switch status
* Countdown timer for picture grab
* Prominent on/off LEDs
* Twitter/Twitpic integration
* IRC integration
* Website integration

Requirements
============
* [tweepy](http://github.com/tweepy/tweepy)
	- setuptools
	- [py_compile](https://groups.google.com/forum/?fromgroups=#!topic/beaglebone/LU6LoEs-zHQ) (missing on the beaglebone Angstrom -.-)
* [oyoyo](https://code.google.com/p/oyoyo/)
* [py-spi](http://www.gigamegablog.com/2012/09/09/beaglebone-coding-101-spi-output/)
* [PyBBIO](https://github.com/alexanderhiam/PyBBIO)
* [ivy-python](http://www.eei.cena.fr/products/ivy/download/checkouts.html)
* [paramiko](https://github.com/paramiko/paramiko/)

Usage
=====
0. Have beaglebone running Angstrom with custom cape and hardware.
1. Edit `twitterbot.ini.example` for your installation parameters.
2. Make sure to rename `twitterbot.ini.example` to `twitterbot.ini`.
3. Start up `manager.py`, which should start up all the other agents.
