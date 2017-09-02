"""
Selfbot for myself. About time.
Created on 3/14/17.
u'\u200b'
This bot has been hijacked by Thane. :^)
"""

import json
import sys
from discord.ext import commands
import discord
import asyncio
import traceback
import logging
from cogs.utils import utils


loop = asyncio.get_event_loop()

app_name = 'selfbot'  # BOT NAME HERE

try:
    with open('redis.json', 'r+') as redis_conf:
        conf = json.load(redis_conf)["db"]
        db = utils.StrictRedis(**conf)
        lconf = conf
        lconf['db'] = 1
except FileNotFoundError:
    db, lconf = None, None  # You're cool, PyCharm, but your warnings can get a bit annoying.
    print('ERROR: redis.json not found in running directory')
    exit()
except:
    db, lconf = None, None
    print('ERROR: could not load configuration')
    exit()

log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename=f'{app_name}.log', encoding='utf-8', mode='a')
formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Instance started.")

config = f'{app_name}:config'
instance = {
    'command_prefix': db.lrange(f'{config}:prefix', 0, -1),
    'status': discord.Status.idle
}
instance.update(db.hgetall(f'{config}:instance'))
bot = commands.Bot(**instance)
bot.db = db
bot.ldb = utils.StrictRedis(**lconf)
bot.app_name = app_name


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(content='This command cannot be used in private messages.')

    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(content='This command is disabled and cannot be used.')

    elif isinstance(error, commands.MissingRequiredArgument):
        await bot.formatter.format_help_for(ctx, ctx.command)

    elif isinstance(error, commands.CommandNotFound):
        await bot.formatter.format_help_for(ctx, ctx.command)

    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        traceback.print_tb(error.__traceback__, file=sys.stderr)
        log.error('In {0.command.qualified_name}:'.format(ctx))
        log.error('{0.__class__.__name__}: {0}'.format(error.original))

    else:
        traceback.print_tb(error.__traceback__, file=sys.stderr)


@bot.event
async def on_member_join(m):
    if m.guild.member_count % 1000 == 0:
        em = discord.Embed(title=m.guild.name,
                           description=f'Guild has reached {m.guild.member_count} members.',
                           color=discord.Colour.green())
        em.set_thumbnail(url=m.guild.icon_url)
        await bot.get_channel(193595671448780800).send(f'$notif {m.guild.name} {m.guild.default_channel.id}', embed=em)


@bot.event
async def on_ready():
    bot.pkmn = bot.get_guild(111504456838819840)
    # app_info = await bot.application_info()  # Bot Only
    # bot.owner = discord.utils.get(bot.get_all_members(), id=app_info.owner.id)  # Bot only
    # await bot.change_presence(game=discord.Game(name=f'{bot.command_prefix[0]}help'))  # Bot only

    print(f'#-------------------------------#\n'
          f'| Successfully logged in.\n'
          f'#-------------------------------#\n'
          f'| Username:  {bot.user.name}\n'
          f'| User ID:   {bot.user.id}\n'
          # f'| Owner:     {bot.owner}\n'  # Bot only
          f'| Guilds:    {len(bot.guilds)}\n'
          f'| Users:     {len(list(bot.get_all_members()))}\n'
          # f'| OAuth URL: {discord.utils.oauth_url(bot.user.id)}\n'  # Bot only
          f'# ------------------------------#')

    print(f'\n'
          f'#-------------------------------#')

    for cog in db.lrange(f'{config}:initial_cogs', 0, -1):
        try:
            print(f'| Loading initial cog {cog}')
            bot.load_extension(f'cogs.{cog}')
            log.info(f'Loaded {cog}')
        except Exception as e:
            log.warning('Failed to load extension {}\n{}: {}'.format(cog, type(e).__name__, e))
            print('| Failed to load extension {}\n|   {}: {}'.format(cog, type(e).__name__, e))

    print(f'#-------------------------------#\n')
    await asyncio.sleep(5)
    await bot.change_presence(afk=True)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


if __name__ == "__main__":
    run = db.hgetall(f'{config}:run')
    bot.run(run['token'], bot=run['bot'])
