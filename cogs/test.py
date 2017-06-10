"""
Trying to trouble shoot the invocation errors
"""

import discord
from discord.ext import commands
from cogs.utils import utils, messages
import inspect


class Test:

    def __init__(self, bot):
        self.bot = bot



    @commands.command(name='ping')
    async def _ping(self, ctx):
        await ctx.channel.send('Pong')



    @commands.command(name='emb')
    async def _embed(self, ctx, *, args):
        # if args is not None:
        import argparse
        # parser = argparse.ArgumentParser()
        # parser.add_argument_group()
        print(list(args))


def setup(bot):
    bot.add_cog(Test(bot))
