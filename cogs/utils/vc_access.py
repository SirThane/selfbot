"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""

import discord
from discord.ext import commands

class VCAccess:

    def __init__(self, bot):
        self.bot = bot

    @bot.event
    async def on_voice_status_update(self, member, before, after):
        if member.guild == 184502171117551617:
            print(dir(member))
            print(dir(before))
            print(dir(after))

def setup(bot):
    bot.add_cog(VCAccess(bot))
