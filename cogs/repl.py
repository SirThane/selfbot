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
        self.store = {}
        self.emb_pag = utils.Paginator(page_limit=1014, trunc_limit=1850, header_extender='Cont.')

    def emb_dict(self, title, desc):
        d = {
            "title": title,
            "description": desc,
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
            'random': random,
            'ret': self.ret,
            'store': self.store
        }
        env.update(globals())
        env.update(self.store)
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
        emb = self.emb_dict(title='Eval on', desc=self.py.format(code))

        try:
            result = eval(code, self.env(ctx))
            if inspect.isawaitable(result):
                result = await result
            self.ret = result
            self.emb_pag.set_headers(['Yielded result:'])
            emb['color'] = 0x00FF00
            for h, v in self.emb_pag.paginate(result):
                field = {
                    'name': h,
                    'value': self.py.format(v),
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
        emb = self.emb_dict(title='Exec on', desc=self.py.format(code))

        try:
            with stdoutio() as s:
                exec(code, self.env(ctx))
                result = str(s.getvalue())
            self.emb_pag.set_headers(['Yielded result:'])
            emb['color'] = 0x00FF00
            for h, v in self.emb_pag.paginate(result):
                field = {
                    'name': h,
                    'value': self.py.format(v),
                    'inline': False,
                }
                emb['fields'].append(field)
        except Exception as e:
            emb['color'] = 0xFF0000
            field = {
                'inline': False,
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': str(e)
            }
            emb['fields'].append(field)

        embed = discord.Embed().from_data(emb)

        await ctx.message.delete()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(REPL(bot))
