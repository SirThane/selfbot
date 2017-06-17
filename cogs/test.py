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

    @commands.command(name='test')
    async def test(self, ctx, member: discord.Member):
        await ctx.send(str(member.id))

    @commands.command(name='emtest')
    async def emtest(self, ctx):
        await ctx.send(embed=discord.Embed(title='test', description='text').add_field(name='test2',
                                                                                       value=discord.Embed.Empty))

    @commands.command(name='getemoji')
    async def getemoji(self, ctx, *, emoji: discord.Emoji=None):
        await ctx.send(emoji if not None else "Didn't work")


def setup(bot):
    bot.add_cog(Test(bot))
