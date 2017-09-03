from discord.ext import commands
from .utils import checks, utils
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
        self.ret = None
        self.emb_pag = utils.Paginator(1014)

    @property
    def emb_dict(self):
        d = {
            "fields": []
        }
        return d

    @property
    def py(self):
        return '```py\n{0}\n```'

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
        emb = self.emb_dict
        emb['title'] = "Eval on:"
        emb['description'] = self.py.format(code)

        try:
            result = eval(code, self.env(ctx))
            if inspect.isawaitable(result):
                result = await result
            self.ret = result
            result = self.emb_pag.paginate(result)
            emb['color'] = 0x00FF00
            field = {
                'name': 'Yielded result:',
                'value': self.py.format(result[0]),
                'inline': False
            }
            emb['fields'].append(field)
            for i in range(1, len(result)):
                field = {
                    'name': "Cont.",
                    'value': self.py.format(result[i]),
                    'inline': False
                }
                emb['fields'].append(field)
        except Exception as e:
            emb['color'] = 0xFF0000
            field = {
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': '{0}'.format(e),
                'inline': False
            }
            emb['fields'].append(field)

        embed = discord.Embed().from_data(emb)

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
