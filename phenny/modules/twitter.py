"""
twitter.py - Twitter Module
Copyright 2013, Andrew G. Meyer
Licensed under the BSD license.

http://github.com/i3detroit/i3Twitbot
"""
#!/usr/bin/env python

import tweepy

def tweet(phenny,input):
    """.tweet text - Tweets the text."""
    auth = tweepy.OAuthHandler(input.consumer_token, input.consumer_secret)
    auth.set_access_token(input.access_token,input.access_secret)
    api = tweepy.API(auth)

    phenny.say('Tweeted "%s"!'%\
               api.update_status(input.group().replace('.tweet','').strip()).text)

tweet.priority = 'medium'
tweet.commands = ['tweet']

def state(phenny,input):
    """.state - replies with the current state of the space."""
    phenny.say('The space is %s'%('closed','open')[True])

state.priority = 'medium'
state.commands = ['state','space','open']
#state.rule = r'*space*open*'

def helloworld(phenny,input):
    phenny.say('Hello, world!')
helloworld.commands = ['hello']
helloworld.priority = 'medium'

if __name__ == "__main__":
        print __doc__.strip()
