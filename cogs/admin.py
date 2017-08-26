"""
Administrative commands for pory. A lot of them used from my HockeyBot,
which in turn were mostly from Danny.
Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import discord
import asyncio
import logging
import os
from .utils import checks

log = logging.getLogger()


class GuildConverter(commands.IDConverter):
    """Converts to a :class:`Guild`.

    All lookups are done via global guild cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID
    2. Lookup by name
    """
    async def convert(self, ctx, argument):
        bot = ctx.bot
        match = self._get_id_match(argument)

        if match is None:
            result = discord.utils.get(bot.guilds, name=argument)
        else:
            guild_id = int(match.group(1))
            result = bot.get_guild(guild_id)

        if not isinstance(result, discord.Guild):
            raise commands.BadArgument('Guild "{}" not found.'.format(argument))

        return result


class UnspecifiedConverter(commands.IDConverter):
    """Converts to any of the following:
    :class:`Guild`, :class:`TextChannel`, :class:`VoiceChannel`,
    :class:`Role`, :class:`Member`, :class:`User`

    all lookups are done via both local and global caches

    the lookup strtegy is as follows (in order):

    1. Guild
    2. Role
    3. TextChannel
    4. VoiceChannel
    5. Member
    6. User
    7. Emoji
    """
    async def convert(self, ctx, argument):
        bot = ctx.bot
        converters = [
            GuildConverter,
            commands.converter.RoleConverter,
            commands.converter.TextChannelConverter,
            commands.converter.VoiceChannelConverter,
            commands.converter.MemberConverter,
            commands.converter.UserConverter,
            commands.converter.EmojiConverter,
        ]
        result = None

        for converter in converters:
            try:
                instance = converter()
                result = await instance.convert(ctx, argument)
                break
            except (commands.BadArgument, commands.NoPrivateMessage):
                continue

        if result is None:
            raise commands.BadArgument(f'Item "{argument}" not found.')

        return result


class Admin:
    """Administrative commands"""
    def __init__(self, bot):
        self.bot = bot

    async def response(self, ctx, message: str, color):

        if self.bot.owner_id:
            await ctx.message.delete()
            resp = await ctx.send(embed=discord.Embed(title=message, color=color))
        else:
            resp = ctx.message
            await ctx.message.edit(embed=discord.Embed(title=message, color=color))
        await asyncio.sleep(3)
        await resp.delete()

    def pull(self):
        resp = os.popen("git pull").read()
        resp = f"```diff\n{resp}\n```"
        return resp

    @commands.command(hidden=True)
    async def load(self, ctx, *, cog: str):
        """load a module"""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await self.response(ctx, '{}: {}'.format(type(e).__name__, e), 0xFF0000)
        else:
            await self.response(ctx, "Module loaded successfully.", 0x00FF00)

    @commands.command(hidden=True)
    async def unload(self, ctx, *, cog: str):
        """Unloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await self.response(ctx, '{}: {}'.format(type(e).__name__, e), 0xFF0000)
        else:
            await self.response(ctx, 'Module unloaded successfully.', 0x00FF00)

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        """Reloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
            await asyncio.sleep(1)
            self.bot.load_extension(cog)
        except Exception as e:
            await self.response(ctx, '{}: {}'.format(type(e).__name__, e), 0xFF0000)
        else:
            await self.response(ctx, 'Module reloaded.', 0x00FF00)

    @commands.command(hidden=True)
    async def superget(self, ctx, *, arg):
        obj = await UnspecifiedConverter().convert(ctx, arg)
        await ctx.send(f"{type(obj).__name__}: {obj}")

    @checks.sudo()
    @commands.command(name="pull", hidden=True)
    async def _pull(self, ctx):
        await ctx.send(embed=discord.Embed(title='Git Pull', description=f"```py\n{self.pull()}\n```"))

    @checks.sudo()
    @commands.command(hidden=True, name='restart', aliases=["kill", "f"])
    async def _restart(self, ctx, *, arg=None):  # Overwrites builtin kill()
        log.warning("Restarted by command.")
        if arg.lower() == "pull":
            resp = self.pull()
        await ctx.send(content=f"{resp}\nRestarting by command. . .")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
