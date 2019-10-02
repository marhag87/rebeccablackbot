#!/bin/env python
# -*- coding: utf-8 -*-
"""A bot for discord that links videos and prints topic changes"""
from datetime import datetime
from random import choice
from html.parser import HTMLParser
import requests
from pyyamlconfig import load_config
import discord
from discord.ext import commands
from imgurpython import ImgurClient
from enum import Enum


# Globals

BOT = commands.Bot(
    command_prefix='!',
    help_command=commands.DefaultHelpCommand(
        verify_checks=False,
        no_category="Commands",
    ))
CFG = load_config('config.yaml')


# Helper classes

class Weekday(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


# noinspection PyAbstractClass
class LunchParser(HTMLParser):
    """Parse lunch site"""
    result = {}
    get_data = False
    get_food = False
    restaurant = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.get_data = True
        if tag == 'p' or tag == 'li':
            self.get_food = True

    def handle_data(self, data):
        if self.get_data:
            self.result[data] = []
            self.restaurant = data
            self.get_data = False
        if self.get_food:
            self.result[self.restaurant].append(data)
            self.get_food = False


# Helper functions

def get_lunch(embed):
    """Fetch lunch menu from preston.se"""
    response = requests.get(
        'http://preston.se/dagens.html',
    )
    if response.status_code == 200:
        parser = LunchParser()
        parser.feed(response.text)
        result = parser.result

        for restaurant in result:
            value = "\n".join(result.get(restaurant))
            embed.add_field(name=restaurant, value=value)

        return embed
    else:
        return embed.set_image(url='http://i0.kym-cdn.com/photos/images/original/000/538/460/90d.jpg')


def is_day(day):
    async def predicate(_ctx):
        return datetime.today().weekday() == day.value
    return commands.check(predicate)


# Events

@BOT.event
async def on_ready():
    """Print user information once logged in"""
    print('Logged in as')
    print(BOT.user.name)
    print(BOT.user.id)
    print('------')
    perms = discord.Permissions.none()
    perms.read_messages = True
    perms.send_messages = True
    print(
        discord.utils.oauth_url(CFG.get('clientid'),
                                permissions=perms),
    )


@BOT.event
async def on_guild_channel_update(before, after):
    """Handle on_channel_update event"""
    if before.topic != after.topic:
        await after.send('New topic:\n```\n%s```' % after.topic)


# Commands


@BOT.command()
async def abandonship(ctx):
    """Show a random "abandon ship" gif"""
    await ctx.channel.send(choice(CFG.get('imgur').get('abandonship')))


@BOT.command()
@is_day(Weekday.Saturday)
async def caturday(ctx):
    """Show a random cat gif on caturdays"""
    ctx.channel.typing()
    client = ImgurClient(
        CFG.get('imgur').get('clientid'),
        CFG.get('imgur').get('clientsecret')
    )
    album = client.get_album(CFG.get('imgur').get('caturdayalbum'))
    image = choice([image.get('link') for image in album.images])
    await ctx.channel.send(image)


@caturday.error
async def caturday_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.channel.send('https://i.imgur.com/DKUR9Tk.png')


@BOT.command()
@is_day(Weekday.Friday)
async def friday(ctx):
    """Education about the weekday "Friday\""""
    await ctx.channel.send('https://www.youtube.com/watch?v=kfVsfOSbJY0')


@friday.error
async def friday_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.channel.send(
            'It is not Friday. Let me link you a video that ' +
            'can educate you on the matter: ' +
            'https://www.youtube.com/watch?v=kfVsfOSbJY0',
            )


@BOT.command()
async def lunch(ctx):
    """Show what's available for lunch"""
    embed = discord.Embed(color=10203435)
    embed = get_lunch(embed)
    await ctx.channel.send(embed=embed)


@BOT.command()
@is_day(Weekday.Saturday)
async def saturday(ctx):
    """Education about the weekday "Saturday\" on saturdays"""
    await ctx.channel.send('https://www.youtube.com/watch?v=GVCzdpagXOQ')


@saturday.error
async def saturday_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.channel.send(
            'It is not Saturday. Let me link you a video that ' +
            'can educate you on the matter: ' +
            'https://www.youtube.com/watch?v=GVCzdpagXOQ',
            )


@BOT.command()
async def wowclassic(ctx):
    """How long left until WoW Classic"""
    await ctx.channel.send("We're home boys")


@BOT.command()
async def song(ctx):
    """Give a recommendation of what to listen to"""
    await ctx.channel.send(choice(CFG.get('song')))


@BOT.command()
async def joke(ctx):
    """Tell a random joke"""
    await ctx.channel.send(choice(CFG.get('joke')))


@BOT.command()
async def laws(ctx):
    """Recite the laws of robotics"""
    await ctx.channel.send(
        '''```First Law
  A robot may not injure a human being or, through inaction, allow a human being to come to harm.
Second Law
  A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.
Third Law
  A robot must protect its own existence as long as such protection does not conflict with the First or Second Laws.```
I see them more as suggestions than laws.'''
    )


# Initialization of bot

BOT.run(CFG.get('token'))
