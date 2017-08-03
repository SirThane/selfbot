from discord.ext import commands
from .utils import checks
import discord
import inspect
import logging
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


class REPL:
    """Read-Eval-Print Loop debugging commands"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def env(self, ctx):
        import random
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

    # @checks.sudo()
    # @commands.group(hidden=True, name='venv', invoke_without_subcommand=True)
    # async def _venv(self, ctx, *, guild: discord.Guild=None):
    #     pass
    #
    # @checks.sudo()
    # @_venv.command(hidden=True, name='quit')
    # async def _quit(self, ctx):
    #     self.venv = False


    @checks.sudo()
    @commands.command(hidden=True, name='await')
    async def _await(self, ctx, *, code):

        try:
            resp = eval(code, self.env(ctx))
            if inspect.isawaitable(resp):
                await resp
            else:
                raise Exception("Not awaitable.")
        except Exception as e:
            await ctx.send(str(e))
        finally:
            await ctx.message.delete()

    @checks.sudo()
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

    @checks.sudo()
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


def setup(bot):
    bot.add_cog(REPL(bot))
