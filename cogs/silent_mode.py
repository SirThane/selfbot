from discord.ext import commands
from asyncio import sleep


class SilentMode:

    def __init__(self, bot):
        self.bot = bot
        self._active = False

    @commands.command(pass_context=True)
    async def toggle_silence(self, ctx):
        self._active = not self._active
        await self.bot.edit_message(ctx.message, "Silent mode {}.".format("enabled" if self._active else "disabled"))
        await sleep(5)
        await self.bot.delete_message(ctx.message)

    async def on_message(self, message):
        if message.author.id == self.bot.user.id and self._active:
            await self.bot.delete_message(message)

