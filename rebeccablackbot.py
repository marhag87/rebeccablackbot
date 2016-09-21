#!/bin/env python
# -*- coding: utf-8 -*-
"""A bot for discord that links videos and prints topic changes"""
import asyncio
import sys
from datetime import datetime
from random import choice
from pyyamlconfig import load_config
import discord
from imgurpython import ImgurClient

CLIENT = discord.Client()

def get_random_caturday_image():
    """Return url to random caturday image from album"""
    client = ImgurClient(
        CFG.get('imgur').get('clientid'),
        CFG.get('imgur').get('clientsecret')
    )
    album = client.get_album(CFG.get('imgur').get('caturdayalbum'))
    return choice([image.get('link') for image in album.images])

def get_days_left(user):
    """Return days left that user has to toil"""
    end_date = CFG.get('daysleft').get(str(user))
    if end_date is None:
        return "http://i.imgur.com/kkrihuR.png"
    else:
        delta = datetime.strptime(end_date, '%Y-%m-%d') - datetime.now()
        return str(delta.days)

@CLIENT.event
async def on_ready():
    """Print user information once logged in"""
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')
    perms = discord.Permissions.none()
    perms.read_messages = True
    perms.send_messages = True
    print(
        discord.utils.oauth_url(CFG.get('clientid'),
        permissions=perms),
    )

@CLIENT.event
async def on_message(message):
    """Handle on_message event"""
    if message.content.startswith('!friday'):
        if datetime.today().weekday() == 4:
            await CLIENT.send_message(
                message.channel,
                'https://www.youtube.com/watch?v=kfVsfOSbJY0',
            )
        else:
            await CLIENT.send_message(
                message.channel,
                'It is not Friday. Let me link you a video that ' +
                'can educate you on the matter: ' +
                'https://www.youtube.com/watch?v=kfVsfOSbJY0',
            )

    if message.content.startswith('!saturday'):
        if datetime.today().weekday() == 5:
            await CLIENT.send_message(
                message.channel,
                'https://www.youtube.com/watch?v=GVCzdpagXOQ',
            )

    if message.content.startswith('!caturday'):
        if datetime.today().weekday() == 5:
            await CLIENT.send_typing(message.channel)
            await CLIENT.send_message(
                message.channel,
                get_random_caturday_image(),
            )
        else:
            await CLIENT.send_message(
                message.channel,
                'https://i.imgur.com/DKUR9Tk.png',
            )

    if message.content.startswith('!daysleft'):
        if message.content == '!daysleft':
            await CLIENT.send_message(
                message.channel,
                "<@%s>: %s" % (message.author.id, get_days_left(message.author)),
            )
        else:
            for user in message.mentions:
                await CLIENT.send_message(
                    message.channel,
                    "<@%s>: %s" % (user.id, get_days_left(user)),
                )

    if CLIENT.user in message.mentions:
        for trigger in CFG.get('abandontriggers'):
            if trigger in message.content.lower():
                await CLIENT.send_message(
                    message.channel,
                    choice(CFG.get('imgur').get('abandonship')),
                )
                break


@CLIENT.event
async def on_channel_update(before, after):
    """Handle on_channel_update event"""
    if before.topic != after.topic:
        await CLIENT.send_message(
            after,
            'New topic:\n```\n%s```' % after.topic,
        )

CFG = load_config('config.yaml')
CLIENT.run(CFG.get('token'))
