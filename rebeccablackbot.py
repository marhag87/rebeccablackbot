#!/bin/env python
# -*- coding: utf-8 -*-
"""A bot for discord that links videos and prints topic changes"""
import asyncio
import sys
from datetime import datetime
import yaml
import discord

def load_config(configfile):
    """Return a dict with configuration from the supplied yaml file."""
    try:
        with open(configfile, 'r') as ymlfile:
            try:
                config = yaml.load(ymlfile)
            except yaml.parser.ParserError:
                print('Could not parse config file: %s' % configfile)
                sys.exit(1)
    except IOError:
        print('Could not open config file: %s' % configfile)
        sys.exit(1)
    return config

CLIENT = discord.Client()

@CLIENT.event
@asyncio.coroutine
def on_ready():
    """Print user information once logged in"""
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')

@CLIENT.event
@asyncio.coroutine
def on_message(message):
    """Handle on_message event"""
    if message.content.startswith('!friday'):
        if datetime.today().weekday() == 4:
            yield from CLIENT.send_message(message.channel,
                                           'https://www.youtube.com/watch?v=kfVsfOSbJY0')
        else:
            yield from CLIENT.send_message(message.channel,
                                           'It is not Friday. Let me link you a video that ' +
                                           'can educate you on the matter: ' +
                                           'https://www.youtube.com/watch?v=kfVsfOSbJY0')

@CLIENT.event
@asyncio.coroutine
def on_channel_update(before, after):
    """Handle on_channel_update event"""
    if before.topic != after.topic:
        yield from CLIENT.send_message(after, 'New topic:\n```\n' + after.topic + '```')

CFG = load_config('config.yaml')
CLIENT.run(CFG.get('token'))
