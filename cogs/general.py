"""General-use cog"""

from discord.ext import commands
from cogs.utils import utils
# from .utils import gizoogle
import discord
from random import randint
# import re
import asyncio

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
    #
    # @commands.command(name="ujd")
    # async def _joined(self, ctx, user: utils.UserType = None):  # MAKE THIS AN EMBED WITH USER AVATAR
    #     """[p]ujd <userid>
    #
    #     Returns member.joined_at for member on current guild."""
    #     svr = ctx.message.author.guild
    #     usr = discord.utils.get(svr.members, id=uid)
    #     if usr is not None:
    #         reply = '```py\n"{0.display_name} ({0})" joined "{1.name}" on:\n{0.joined_at}\n```'.format(usr, svr)
    #         await ctx.message.edit(reply)
    #     else:
    #         await ctx.message.edit('```py\nUser {0} is not a member of {1.name}\n```'.format(uid, svr))
    #         try:
    #             await self.bot.add_reaction(ctx.message, "\N{THUMBS UP SIGN}")
    #         except AttributeError:
    #             await self.bot.delete_message(ctx.message)

    @commands.command(aliases=['getuserinfo', 'userinfo'], no_private=True)
    async def _getuserinfo(self, ctx, member: discord.Member=None):
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

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': '{0.name}#{0.discriminator}'.format(member),
                'color': getattr(discord.Colour, member.default_avatar.name)()
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
    async def pressf(self, ctx):
        await ctx.message.delete()
        await ctx.send('**[Press F to RIP]**')
        msg = await ctx.send(':pressf:')
        await msg.add_reaction(u'👆')

    @commands.command(name='learnpy')
    async def learnpy(self, ctx):
        await ctx.message.delete()
        msg = """
Well, I started here and everyone said I shouldn't bother with it because it has an old Python version, but for someone who's not just new to Python, but new to programming in general, use https://codecademy.com/.
It's very interactive, and even though you can't really do anything with what you learn, it will familiarize you with the fundamentals.
It's free. There are some other resources that you can use afterwards, but I would suggest starting here.
http://python.swaroopch.com/ (for complete beginners to programming)
https://learnxinyminutes.com/docs/python3/ (for people who know programming already)
https://docs.python.org/3.5/tutorial/ (for the in-between group, i.e. knows some programming but not a lot)
see also: http://www.codeabbey.com/ (exercises for beginners)
http://www.learnpython.org/ (somewhat interactive tutorial)
Also, this guy's video tutorials are excellent.
https://www.youtube.com/playlist?list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7
https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU
https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc
"""
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(General(bot))
