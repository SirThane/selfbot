"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""

import discord
from discord.ext import commands
# import main

class VCAccess:

    def __init__(self, bot):
        self.bot = bot

    @property
    def guild(self):
        return self.bot.get_guild(184502171117551617)

    @property
    def channel(self):
        return self.guild.get_channel(315232431835709441)

    async def on_voice_state_update(self, member, before, after):
        dir(member)
        dir(before)
        dir(after)
        await self.channel.send(content=dir(member))


def setup(bot):
    bot.add_cog(VCAccess(bot))
