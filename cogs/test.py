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

    @commands.command(name='emb')
    async def _embed(self, ctx, *, args):
        # if args is not None:
        import argparse
        # parser = argparse.ArgumentParser()
        # parser.add_argument_group()
        print(list(args))

    @commands.command()
    async def _userinfo(self, ctx, member: utils.UserType=None):
        """Get a user's information"""

        message = ctx.message
        if message.mentions:  # Needs to be that way or things don't work
            member = message.mentions[0]
        elif member is not None:
            member = ctx.message.guild.get_member(member.user_id)
        else:
            member = message.author

        # joined_at gives us a UTC timestamp (in datetime form)
        # Tried changing it to PST, but it's just too much of a hassle so we'll just leave it how it is
        joined_ts = member.joined_at.strftime("%Y-%m-%d %H:%M")
        created_ts = member.created_at.strftime("%Y-%m-%d %H:%M")
        user_info = messages.user_info.format(member,
                                              str([r.name for r in member.roles if r.name != "@everyone"]).strip("[]"),
                                              joined_ts,
                                              created_ts)
        await ctx.send(user_info)


def setup(bot):
    bot.add_cog(Test(bot))
