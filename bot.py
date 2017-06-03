"""
Selfbot for myself. About time.
Created on 3/14/17.

This bot has been hijacked by Thane. :^)
"""

import json
import logging
import sys
from cogs.utils.config import Config
from discord.ext import commands
import asyncio
import traceback

loop = asyncio.get_event_loop()

log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')
formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Instance started.")

prefix = [">>> "]

initial_extensions = [
    "cogs.admin",
    "cogs.general",
    "cogs.test"
]

description = "me irl"

try:
    with open('auth.json', 'r+') as json_auth_info:
        auth = json.load(json_auth_info)
        token = auth["discord"]["token"]
except IOError:
    sys.exit("auth.json not found in running directory.")

bot = commands.Bot(command_prefix=prefix, description=description, pm_help=True, self_bot=True)


@bot.listen()
async def timer_update(seconds):
    # Dummy listener
    return seconds


async def init_timed_events(bot):
    """Create a listener task with a tick-rate of 1s"""

    await bot.wait_until_ready()  # Wait for the bot to launch first

    secs = 0  # Keep track of the number of secs so we can access it elsewhere and adjust how often things run
    while True:
        bot.dispatch("timer_update", secs)
        await timer_update(secs)
        secs += 1
        bot.secs = secs
        await asyncio.sleep(1)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.edit_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'This command is disabled and cannot be used.')
    elif isinstance(error, commands.MissingRequiredArgument):
        help_formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel,
                               "You are missing required arguments.\n{}".format(help_formatter.format_help_for(ctx, ctx.command)[0]))
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__, file=sys.stderr)
        log.error('In {0.command.qualified_name}:'.format(ctx))
        log.error('{0.__class__.__name__}: {0}'.format(error.original))
    else:
        traceback.print_tb(error.original.__traceback__, file=sys.stderr)
        # traceback.print_tb(error, file=sys.stderr)
        # print("on_command_error was triggered.")
        # print(error.args)
        # print(error.kwargs)
        # print(ctx.args)
        # print(ctx.kwargs)
        # str(error)
        # print(dir(error))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    log.info("Initialized.")

    print('------')


@bot.event
async def on_message(message):
    await bot.process_commands(message)

# bot.config = Config("config.json")

# Starting up

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            log.info("Loaded {}".format(extension))
        except Exception as e:
            log.warning('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

        bot.run(token, bot=False)
