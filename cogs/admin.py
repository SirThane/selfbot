"""
Administrative commands for pory. A lot of them used from my HockeyBot,
which in turn were mostly from Danny.
Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import traceback
import inspect
import logging
from asyncio import sleep

log = logging.getLogger()


class Admin:

    def __init__(self, bot):
        self.bot = bot
        # self.config = bot.config

    @commands.command(hidden=True)
    async def load(self, ctx, *, cog: str, verbose: bool=False):
        """load a module"""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            if not verbose:
                await ctx.message.edit(content='{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.message.edit(content=traceback.print_tb(e.__traceback__))
        else:
            await ctx.message.edit(content="Module loaded successfully.")

    @commands.command(hidden=True)
    async def unload(self, ctx, *, cog: str):
        """Unloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.message.edit(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.edit(content='Module unloaded successfully.')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        """Reloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
            sleep(1)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.message.edit(content='Failed.')
            sleep(1)
            await ctx.message.edit(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.edit(content='Module reloaded.')

    @commands.command(hidden=True, name='await')
    async def _await(self, ctx, *, code):
        import discord

        try:
            result = await code
            await ctx.send(result)
        except Exception as e:
            await ctx.send(str(e))
        else:
            await ctx.message.delete()

    # Thanks to rapptz
    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, code: str):
        """Run eval() on an input."""
        import discord
        import random
        code = code.strip('` ')
        python = '```py\n{0}\n```'
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

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
            emb = {
                'color': 0xFF0000,
                'field': {
                    'name': 'Yielded result:',
                    'value': python.format(result),
                    'inline': False
                }
            }
        except Exception as e:
            emb = {
                'color': 0x00FF00,
                'field': {
                    'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                    'value': '{0} '.format(e),
                    'inline': False
                }
            }

        embed = discord.Embed(title="Eval on:", description=python.format(code), color=emb['color'])
        embed.add_field(**emb['field'])

        await ctx.message.delete()
        await ctx.channel.send(embed=embed)
        # await ctx.message.edit(content='', embed=embed)

    @commands.command(hidden=True, name='exec')
    async def _exec(self, ctx, *, code: str):
        """Run eval() on an input."""
        import asyncio
        import discord
        import random
        code = code.strip('```\n ')
        python = '```py\n{0}{1}\n```'
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'asyncio': asyncio,
            'discord': discord,
            'random': random
        }

        env.update(globals())

        try:
            result = exec(code, env)
            if inspect.isawaitable(result):
                result = await result
            emb = {
                'color': 0x00ff00,
                'field': {
                    'name': 'Yielded result:',
                    'value': python.format('', result),
                    'inline': False
                }
            }
        except Exception as e:
            emb = {
                'color': 0xff0000,
                'field': {
                    'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                    'value': str(e),
                    'inline': False
                }
            }

        embed = discord.Embed(title="Exec on:", description=python.format('>>> ', code), color=emb['color'])
        embed.add_field(**emb['field'])

        await ctx.message.delete()  # FOR SOME REASON THIS DELETES THE MESSAGE *AND* THE MESSAGE BEFORE IT.
        await ctx.channel.send(embed=embed)

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
