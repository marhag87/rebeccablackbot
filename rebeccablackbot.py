#!/bin/env python
import discord
import asyncio
from datetime import datetime
import yaml
import sys

configfile = 'config.yaml'
try:
  with open(configfile, 'r') as ymlfile:
    try:
      cfg = yaml.load(ymlfile)
    except yaml.parser.ParserError:
      print('Could not parse config file: %s' % configfile)
      sys.exit(1)
except IOError:
  print('Could not open config file: %s' % configfile)
  sys.exit(1)

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

@client.event
@asyncio.coroutine
def on_message(message):
  if message.content.startswith('!friday'):
    if datetime.today().weekday() == 4:
      yield from client.send_message(message.channel, 'https://www.youtube.com/watch?v=kfVsfOSbJY0')
    else:
      yield from client.send_message(message.channel, 'It is not Friday. Let me link you a video that can educate you on the matter: https://www.youtube.com/watch?v=kfVsfOSbJY0')

@client.event
@asyncio.coroutine
def on_channel_update(before, after):
  if before.topic != after.topic:
    yield from client.send_message(after, 'New topic:\n```\n' + after.topic + '```')

client.run(cfg.get('username'), cfg.get('password'))
