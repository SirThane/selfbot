# import json
# import logging
# import sys
# # from cogs.utils.config import Config
# from discord.ext import commands
# import discord
# import asyncio
# import traceback
#
# loop = asyncio.get_event_loop()
#
# log = logging.getLogger()
# log.setLevel(logging.WARNING)
# handler = logging.FileHandler(filename='selfbot.log', encoding='utf-8', mode='a')
# formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{")
# handler.setFormatter(formatter)
# log.addHandler(handler)
#
# log.info("Instance started.")
#
# prefix = [">>> "]
#
# initial_extensions = [
#     'admin',
#     'general',
#     'test'
# ]
#
# description = "me irl"
#
# try:
#     with open('auth.json', 'r+') as json_auth_info:
#         auth = json.load(json_auth_info)
#         token = auth["discord"]["token"]
# except IOError:
#     sys.exit("auth.json not found in running directory.")
#
# bot = commands.Bot(command_prefix=prefix, description=description, pm_help=True, self_bot=True,
#                    status=discord.Status.idle)
#
#
# @bot.listen()
# async def timer_update(seconds):
#     # Dummy listener
#     return seconds
#
#
# async def init_timed_events(bot):
#     """Create a listener task with a tick-rate of 1s"""
#
#     await bot.wait_until_ready()  # Wait for the bot to launch first
#
#     secs = 0  # Keep track of the number of secs so we can access it elsewhere and adjust how often things run
#     while True:
#         bot.dispatch("timer_update", secs)
#         await timer_update(secs)
#         secs += 1
#         bot.secs = secs
#         await asyncio.sleep(1)
#
#
# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.NoPrivateMessage):
#         await ctx.message.channel.send(content='This command cannot be used in private messages.')
#
#     elif isinstance(error, commands.DisabledCommand):
#         await ctx.message.channel.send(content='This command is disabled and cannot be used.')
#
#     elif isinstance(error, commands.MissingRequiredArgument):
#         help_formatter = commands.formatter.HelpFormatter()
#         await ctx.message.channel.send(content=\
#             "You are missing required arguments.\n{}".format(help_formatter.format_help_for(ctx, ctx.command)[0]))
#
#     elif isinstance(error, commands.CommandNotFound):
#         # await self.bot.add_reaction(ctx.message, "{X}")
#         await ctx.message.channel.send(content="Command not found")
#
#     elif isinstance(error, commands.CommandInvokeError):
#         print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
#         print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
#         traceback.print_tb(error.__traceback__, file=sys.stderr)
#         log.error('In {0.command.qualified_name}:'.format(ctx))
#         log.error('{0.__class__.__name__}: {0}'.format(error.original))
#
#     else:
#         traceback.print_tb(error.original.__traceback__, file=sys.stderr)
#
#
# @bot.event
# async def on_ready():
#     print('Logged in as')
#     print(bot.user.name)
#     print(bot.user.id)
#     log.info("Initialized.")
#
#     print('------')
#     await asyncio.sleep(5)
#     await bot.change_presence(afk=True)
#     print('AFK status set.')
#     # global home_guild
#     # home_guild = discord.utils.get(bot.guilds, id=184502171117551617)
#     # global me_
#     # me_ = discord.utils.get(home_guild.channels, id=193595671448780800)
#     # print('Owned guild and #me_ set. Mention detector available.')
#
#
# @bot.event
# async def on_message(message):
#     # if me_ and not isinstance(message.channel, discord.DMChannel) and message.author.id != bot.user.id:
#     #     l = ['thane', 'sir thane', 'sirthane']
#     #     l.append(message.guild.me.display_name.lower())
#     #     if any(map(lambda x: x in message.content.lower(), l)):
#     #         timestamp = datetime.utcnow().strftime("%b. %d, %Y %I:%M %p")
#     #         display_name = f' ({message.author.display_name})' \
#     #                        if message.author.display_name != message.author.name else ''
#     #         em = discord.Embed(title='{0.guild}: #{0.channel} at {1}'.format(message, timestamp),
#     #                            description=message.content,
#     #                            color=message.author.color)
#     #         em.set_author(name='{0.name}#{0.discriminator}{1}'.format(message.author, display_name),
#     #                       icon_url=message.author.avatar_url_as(format='png'))
#     #         await me_.send(f'$self_mention_detected    {message.channel.id}', embed=em)
#     await bot.process_commands(message)
#
# # Starting up
#
# if __name__ == "__main__":
#     print()
#     for extension in initial_extensions:
#         try:
#             print("Loading initial cog 'cogs.{}'".format(extension))
#             bot.load_extension('cogs.{}'.format(extension))
#             log.info("Loaded cogs.{}".format(extension))
#         except Exception as e:
#             log.warning('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
#             print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
#
#     print()
#     bot.run(token, bot=False)
#     bot.change_presence(afk=True)

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
except FileNotFoundError:
    print('ERROR: redis.json not found in running directory')
    exit()
except:
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


me_channel = bot.get_channel(id=193595671448780800)


@bot.event
async def on_member_join(m):
    if m.guild.member_count % 1000 == 0:
        em = discord.Embed(title=m.guild.name,
                           description=f'Guild has reached {m.guild.member_count} members.',
                           color=discord.Colour.green())
        await me_channel.send(f'$notif {m.guild.default_channel}', embed=em)


@bot.event
async def on_ready():
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
