"""
Trying to trouble shoot the invocation errors
"""

import discord
from discord.ext import commands
import inspect

class Test:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='ping')
    async def ping(self, ctx):
        await ctx.message.channel.send('Pong')

    @commands.command(name='test')
    async def test(self, ctx, *, code: str):
        code = code.strip('``` ')
        print(code)

    # Thanks to rapptz
    @commands.command(hidden=True, name='exec')
    async def _exec(self, ctx, *, code: str):
        """Run eval() on an input."""
        import asyncio
        import discord
        import random
        code = code.strip('``` ')
        python = '```py\n{0}\n```'
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
            # if inspect.isawaitable(result):
            #     result = await result
            emb = {
                'color': 0x00ff00,
                'field': {
                    'name': 'Yielded result:',
                    'value': python.format(result),
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

        embed = discord.Embed(title="Exec on:", description=python.format(code), color=emb['color'])
        embed.add_field(**emb['field'])

        await ctx.message.delete()  # FOR SOME REASON THIS DELETES THE MESSAGE *AND* THE MESSAGE BEFORE IT.
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Test(bot))
