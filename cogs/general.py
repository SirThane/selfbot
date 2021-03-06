"""General-use cog"""

from discord.ext import commands
from cogs.utils import utils
# from .utils import gizoogle
import discord
from random import randint
# import re
import asyncio
import argparse

from urllib.parse import urlencode


class General:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def lmgtfy(self, ctx, *, link: str):
        """Gives a lmgtfy link to an input."""
        params = {"q": link}
        await ctx.message.edit(content="http://lmgtfy.com/?{0}".format(urlencode(params)))

    # @commands.command(pass_context=True)
    # async def giz(self, ctx, *, text: str):
    #     """Get a gizooglified version of some text."""
    #     if re.match(r'^((http[s]?|ftp):/)?/?([^:/\s]+)((/\w+)*/)([\w\-.]+[^#?\s]+)(.*)?(#[\w\-]+)?$',
    #                 text):
    #         # if we get a url input
    #         giz_output = await gizoogle.Website.translate(text)
    #     else:
    #         giz_output = await gizoogle.String.translate(text)
    #     await self.bot.edit_message(ctx.message, giz_output)

    @commands.command(pass_context=True, aliases=["rolld"])
    async def roll(self, ctx, sides: int, rolls: int = 1):
        """Roll a die, or a few."""

        if rolls == 1:  # Just !roll 3
            num = randint(1, abs(sides))
            await ctx.message.edit(content="Rolled {}".format(num))

        else:  # !roll 3 4
            max_rolls = 30
            output = ""
            if rolls > max_rolls:
                output += "Too many dice rolled, rolling {} instead.\n".format(max_rolls)
                rolls = max_rolls

            elif rolls < 0 or sides < 1:
                await ctx.message.edit(content="Value too low.")
                return

            output += "Rolling {}d{}:\n".format(rolls, sides)
            for roll in range(rolls):
                roll_result = randint(1, sides)
                output += "`{}` ".format(roll_result)

            await ctx.message.edit(content=output)

    @commands.command(pass_context=True)
    async def ri(self, ctx, *, text: str):
        output = ""
        for char in text:
            if char == "b":
                output += ":b:"
            elif char.isalpha():
                output += ":regional_indicator_{}: ".format(char.lower())
            else:
                output += char

        await ctx.message.edit(content=output)

    @commands.command(aliases=["game"])
    async def set_game(self, ctx, *, game: str=None):
        if game:
            await self.bot.change_presence(game=discord.Game(name=game))
        else:
            await self.bot.change_presence(game=None)
        await ctx.message.edit(content="```\nGame set to {}.```".format(game))

    @commands.command(pass_context=True)
    async def purge(self, ctx, messages: int=-1):
        async for message in self.bot.logs_from(ctx.message.channel, limit=messages if messages > 0 else None):
            await self.bot.delete_message(message)
            await asyncio.sleep(2)

    # async def on_message(self, message):
    #
    #     # print(message.content)
    #
    #     if re.search("((?:[ls]uc)|(?:canine dicks?))(?!\w)", message.content.lower()):
    #         embed = discord.Embed(title="You were mentioned in {}.".format(message.channel.name))
    #         embed = format_embed(embed, message.author)
    #         embed.add_field(name="Server", value=message.guild.name)
    #         embed.add_field(name="Content", value=message.content)
    #
    #
    #         if message.attachments:
    #             embed.set_image(message.attachments[0])
    #
    #         await self.bot.send_message(discord.Object(id="291451280902193152"),
    #                                     "M*)(B8mdu98vuw09vmdfj",
    #                                     embed=embed)

    @commands.command(name='userinfo', no_private=True)
    async def userinfo(self, ctx, *, member: discord.Member=None):
        """Gets current server information for a given user

        Usage:  $userinfo @user
                $userinfo username#discrim
                $userinfo userid

        Issues: Some special characters cause problems when
                using un#dis. For those, mention or userid
                should still work."""

        from datetime import datetime

        if member is None:
            member = ctx.message.author

        roles = str([r.name for r in member.roles if '@everyone' not in r.name]).strip('[]').replace(', ', '\n').replace("'", '')
        if roles == '':
            roles = 'User has no assigned roles.'

        timestamp = datetime.utcnow().strftime("%b. %d, %Y %I:%M %p")

        if member.default_avatar.name == 'grey':
            color = discord.Colour.light_grey()
        else:
            color = getattr(discord.Colour, member.default_avatar.name)()

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': '{0.name}#{0.discriminator}'.format(member),
                'color': color
            },
            'author': {
                'name': '{0.name}  ||  #{1.name}'.format(ctx.guild, ctx.channel),
                'icon_url': ctx.guild.icon_url
            },
            'fields': [
                {
                    'name': 'User ID',
                    'value': str(member.id),
                    'inline': True
                },
                {
                    'name': 'Display Name:',
                    'value': member.display_name if not None else '(no display name set)',
                    'inline': True
                },
                {
                    'name': 'Roles:',
                    'value': roles,
                    'inline': False
                },
                {
                    'name': 'Account Created:',
                    'value': member.created_at.strftime("%b. %d, %Y\n%I:%M %p"),  # ("%Y-%m-%d %H:%M"),
                    'inline': True
                },
                {
                    'name': 'Joined Server:',
                    'value': member.joined_at.strftime("%b. %d, %Y\n%I:%M %p"),
                    'inline': True
                },
            ],
            'footer': {
                'text': 'Invoked by {0.name}#{0.discriminator}  ||  {1}'.format(ctx.message.author, timestamp),
                'icon_url': ctx.message.author.avatar_url
            }
        }

        embed = discord.Embed(**emb['embed'])  # TODO: EMBED FUNCTION/CLASS
        embed.set_author(**emb['author'])
        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        for field in emb['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb['footer'])

        await ctx.channel.send(embed=embed)

    # @commands.command(name='illegal')
    # async def isnowillegal(self, ctx, *, phrase=None):
    #     """Make President Trump declare something illegal"""
    #
    #     import requests
    #     import json
    #
    #     if phrase is None:
    #         phrase = ctx.author.name
    #     if len(phrase) > 10:
    #         em = discord.Embed(title="Too Long", description="We all know Trump is stupid. He can't process that",
    #                            colour=discord.Color.green())
    #         await ctx.send(embed=em)
    #         return
    #     url = "https://is-now-illegal.firebaseio.com/queue/tasks.json"
    #
    #     payload = {"task": "gif", "word": phrase.replace(" ", "%20").upper()}
    #     payload = json.dumps(payload)
    #     headers = {'content-type': "application/json", 'cache-control': "no-cache", }
    #
    #     response = requests.request("POST", url, data=payload, headers=headers)
    #
    #     print(response.text)
    #     m = await ctx.send(
    #         embed=discord.Embed(title="Generating...", description="Please wait (This may take up to 30 seconds)"))
    #     phrase = phrase.replace(" ", "%20").upper()
    #     await asyncio.sleep(20)
    #
    #     url = f"https://is-now-illegal.firebaseio.com/gifs/{phrase.upper()}.json"
    #
    #     headers = {'content-type': "application/json", 'cache-control': "no-cache", }
    #
    #     response = requests.request("GET", url, data=payload, headers=headers)
    #     print(response.text)
    #
    #     r = json.loads(response.text)
    #     if r is None:
    #         await self.bot.say(embed=discord.Embed(title="Error with isnowillegal API",
    #                                                description="If you want you can go [here](http://isnowillegal.com)"
    #                                                            "and make the gif yourself"))
    #         return
    #     url = r['url']
    #     em = discord.Embed(title="Is Now Illegal", colour=discord.Color.green())
    #     em.set_image(url=url)
    #     await ctx.send(embed=em)

    @commands.command(name='pressf')
    async def pressf(self, ctx, *, to: str=None):
        await ctx.message.delete()
        if not to:
            to = "RIP"
        await ctx.send(f'**[Press F to {to}]**')
        msg = await ctx.send('<:pressf:327966024919941120>')
        await msg.add_reaction(u'👆')

    @commands.command(name='unlocked')
    async def unlocked(self, ctx, *, msg):
        emb = discord.Embed(description=f"<:xbox:285631858400559104> **Achievement Unlocked**: {msg}",
                            color=discord.Colour.green())
        await ctx.message.delete()
        await ctx.send(embed=emb)

    @commands.command(name='emoji')
    async def emoji(self, ctx, *, emoji: discord.Emoji):
        emb = discord.Embed(title=f'{emoji.name} ({emoji.id})', url=f'{emoji.url}',
                            description=f'From guild: {emoji.guild}',
                            color=ctx.guild.me.color)
        emb.set_image(url=emoji.url)
        emb.set_footer(text=emoji.url)
        await ctx.send(embed=emb)

    @commands.command(name='boou')
    async def boou(self, ctx, *, target: str):
        """Boo dat guy, but with S T Y L E"""
        chars = {'1': ':one:', '2': ':two:', '3': ':three:', '4': ':four:', '5': ':five:',
                 '6': ':six:', '7': ':seven:', '8': ':eight:', '9': ':nine:', '0': ':zero:'}
        chars.update({c: f":regional_indicator_{c}:" for c in list('abcdefghijklmnopqrstuvwxyz')})

        lines = target.lower().split(' ')

        invalid = []
        for line in lines:
            for char in line:
                if char not in chars.keys():
                    invalid.append(char)
        if invalid:
            await ctx.send(f"Invalid character(s): {', '.join('(**{}**)'.format(invalid))}")
            return

        emojis = self.bot.get_guild(146626123990564864).emojis
        emojis = [discord.utils.get(emojis, name=n) for n in ["boou", "boou2", "boou3", "boou4", "boo"]]
        chars[' '] = emojis[4]

        def add_line(line):
            return f"{emojis[4]}{''.join([f'{emojis[i % 4]}{line[i]}' for i in range(len(line))])}" \
                   f"{emojis[len(line) % 4]}{emojis[4]}"

        m = max(map(len, lines))

        for i in range(len(lines) - 1):
            try:
                if len(lines[i]) + len(lines[i + 1]) + 1 <= m:
                    lines[i] += f" {lines.pop(i + 1)}"
            except IndexError:
                break

        lines = [[chars[c.lower()] for c in line] + ([emojis[4]] * (m - len(line))) for line in lines]

        resp = u"\n{}\n\u200b".format('\n'.join(list(map(add_line, lines)))).join([add_line([emojis[4]] * m)] * 2)

        await ctx.message.delete()

        for l in utils.Paginator(page_limit=2000, trunc_limit=8000).paginate(str(resp)):
            await ctx.send(l)
            await asyncio.sleep(0.1)

    @commands.command(name='embed')
    async def _embed(self, ctx, *, args: str=None):
        args = args.split()
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--title", help="Embed Title")
        parser.add_argument("-d", "--description", help="Embed Description")
        parser.add_argument("-c", "--color", help="Embed Color")
        parsed = parser.parse_args(args)
        await ctx.send(f"{type(parsed)}: {parsed}")

def setup(bot):
    bot.add_cog(General(bot))
