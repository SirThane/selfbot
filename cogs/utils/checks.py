"""Simulate .utils.checks so cogs can be
transferred between bots and selfbots
without removing checks decorators"""

from discord.ext import commands


def sudo():
    def predicate(ctx):
        return True
    return commands.check(predicate)
