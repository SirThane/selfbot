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

    @commands.command(name='tost')
    async def _tost(self, ctx, member: discord.Member=None):
        await ctx.channel.send(member.color)

    @commands.command(name='dacolor')
    async def _dacolor(self, ctx, member: discord.Member=None):

        if member is None:
            member = ctx.message.author

        default_avatar = member.default_avatar.name
        color = getattr(discord.Colour, default_avatar)()

        await ctx.send(embed=discord.Embed(title=default_avatar, colour=color))

    @commands.command(name='emb')
    async def _embed(self, ctx, *, args):
        # if args is not None:
        import argparse
        # parser = argparse.ArgumentParser()
        # parser.add_argument_group()
        print(list(args))


def setup(bot):
    bot.add_cog(Test(bot))
