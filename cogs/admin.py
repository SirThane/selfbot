"""
Administrative commands for pory. A lot of them used from my HockeyBot,
which in turn were mostly from Danny.
Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import discord
import asyncio
import logging

log = logging.getLogger()


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

    # @commands.command(hidden=True, name='set_config')
    # async def _set_config(self, ctx, key: str, value: str):
    #     """Directly alter a config file."""
    #     try:
    #         try:
    #             value = int(value)
    #         except ValueError:
    #             pass
    #         await self.config.put(key, value)
    #         await ctx.message.edit(content="Success.")
    #     except KeyError:
    #         raise commands.CommandInvokeError
    #
    # @commands.command(hidden=True, name='append_to_config')
    # async def _append_to_config(self, ctx, key: str, value: str):
    #     """Append a value to a list in a config file"""
    #     try:
    #         temp_list = await self.config.get(key)
    #         temp_list.append(value)
    #         await self.config.put(key, temp_list)
    #         await ctx.message.edit(content="Success.")
    #     except KeyError:
    #         await ctx.message.edit(content="Key {} not found.".format(key))

    @commands.command(hidden=True, aliases=["rip", "F", "f"])
    async def kill(self, ctx):  # Overwrites builtin kill()
        log.warning("Restarted by command.")
        await ctx.message.edit(content="Restarting.")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
