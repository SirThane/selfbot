"""General-use cog"""

from discord.ext import commands
from .utils.utils import format_embed
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

    @commands.command(name='obj')
    async def _obj(self, ctx, arg_obj):
        """Helper command to get information about an object."""
        await ctx.message.channel.send(content='{0.name}\n{1}\n{0.id}'.format(arg_obj, dir(arg_obj)))

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

    @commands.command(name="ujd")
    async def _joined(self, ctx, user: any): ### MAKE THIS AN EMBED WITH USER AVATAR
        """[p]ujd <userid>

        Returns member.joined_at for member on current guild."""
        svr = ctx.message.author.guild
        usr = discord.utils.get(svr.members, id=uid)
        if usr is not None:
            reply = '```py\n"{0.display_name} ({0})" joined "{1.name}" on:\n{0.joined_at}\n```'.format(usr, svr)
            await ctx.message.edit(content=reply)
        else:
            await ctx.message.edit(content='```py\nUser {0} is not a member of {1.name}\n```'.format(uid, svr))
            try:
                await self.bot.add_reaction(ctx.message, "\N{THUMBS UP SIGN}")
            except AttributeError:
                await self.bot.delete_message(ctx.message)

    @commands.command(name='gui')
    async def gui(self, ctx, uid: int):
        await ctx.message.channel.send(content=self.bot.get_user_info(uid))


def setup(bot):
    bot.add_cog(General(bot))
