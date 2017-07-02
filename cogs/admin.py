"""
Administrative commands for pory. A lot of them used from my HockeyBot,
which in turn were mostly from Danny.
Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import discord
import asyncio
import random
import traceback
import inspect
import logging
from asyncio import sleep
import sys
from io import StringIO
import contextlib

log = logging.getLogger()


@contextlib.contextmanager
def stdoutio(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class Admin:
    """Administrative commands"""
    def __init__(self, bot):
        self.bot = bot
        # self.config = bot.config

    async def response(self, ctx, message: str, color):

        if self.bot.owner_id:
            await ctx.message.delete()
            resp = await ctx.send(embed=discord.Embed(title=message, color=color))
        else:
            resp = ctx.message
            await ctx.message.edit(embed=discord.Embed(title=message, color=color))
        await asyncio.sleep(3)
        await resp.delete()

    def env(self, ctx):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
            'random': random
        }
        env.update(globals())
        return env

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

    @commands.command(hidden=True, name='await')
    async def _await(self, ctx, *, code):

        try:
            resp = eval(code)
            if inspect.isawaitable(resp):
                await resp
        except Exception as e:
            await ctx.send(str(e))
        finally:
            await ctx.message.delete()

    # Thanks to rapptz
    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, code: str):
        """Run eval() on an input."""

        code = code.strip('` ')
        python = '```py\n{0}\n```'

        try:
            result = eval(code, self.env(ctx))
            if inspect.isawaitable(result):
                result = await result
            result = str(result)[:1014]
            color = 0x00FF00
            field = {
                'name': 'Yielded result:',
                'value': python.format(result),
                'inline': False
            }
        except Exception as e:
            color = 0xFF0000
            field = {
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': '{0} '.format(e),
                'inline': False
            }

        embed = discord.Embed(title="Eval on:", description=python.format(code), color=color)
        embed.add_field(**field)

        await ctx.message.delete()
        await ctx.channel.send(embed=embed)

    @commands.command(hidden=True, name='exec')
    async def _exec(self, ctx, *, code: str):
        """Run exec() on an input."""

        code = code.strip('```\n ')
        python = '```py\n{0}\n```'

        try:
            with stdoutio() as s:
                exec(code, self.env(ctx))
                result = str(s.getvalue())
            result = str(result)[:1014]
            color = 0x00FF00
            field = {
                'inline': False,
                'name': 'Yielded result(s):',
                'value': python.format(result)
            }
        except Exception as e:
            color = 0xFF0000
            field = {
                'inline': False,
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': str(e)
            }

        embed = discord.Embed(title="Exec on:", description=python.format(code), color=color)
        embed.add_field(**field)

        await ctx.message.delete()
        await ctx.send(embed=embed)

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
