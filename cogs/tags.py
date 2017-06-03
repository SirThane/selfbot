"""Basic tag support"""

from discord.ext import commands
from .utils import checks, utils


class Tags:

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.group(invoke_without_command=True, pass_context=True)
    async def tag(self, ctx, name: str):  # Should maybe be how to expect an argument
        try:
            tag = self.config.get(name)
        except KeyError:
            await self.bot.delete_message(ctx.message)
            return

        await self.bot.say(tag)

    @tag.command(pass_context=True)
    async def add(self, ctx, name: str, *, content: str):
        # TODO: Make generic errors for these commands like how robodanny does it

        if utils.check_input(name) or utils.check_mentions(content):
            await self.bot.say("Invalid tag info")
        elif len(name) > 30:
            await self.bot.say("Tag name must be less than 30 characters.")
        elif len(content) > 200:
            await self.bot.say("Tag content must be less than 200 characters.")
        else:
            await self.config.put(name, content)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.bot.say(str(error))  # I have no idea how this will work


def setup(bot):
    bot.add_cog(Tags(bot))
