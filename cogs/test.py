"""
Trying to trouble shoot the invocation errors
"""

import discord
from discord.ext import commands

class Test:

    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def ping(self, ctx):
        await self.bot.message.channel.send("Pong")

def setup(bot):
    bot.add_cog(Test(bot))
