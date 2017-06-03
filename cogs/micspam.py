"""Micspam"""
import asyncio
import glob
import logging
import discord
from discord.ext import commands
from sys import stderr


log = logging.getLogger()


class Micspam:

    def __init__(self, bot):

        self.bot = bot
        self.voice_client = None

    @staticmethod
    def get_micspam(clip_chosen, song_list):
        try:
            return song_list[clip_chosen]
        except IndexError:
            return None

    def micspam_after(self, voice_client):
        coro = voice_client.disconnect()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except Exception as e:
            # an error happened
            print("Error occured in future")
            print('{0.__class__.__name__}: {0}'.format(e), file=stderr)

    async def play_micspam(self, ctx, song_id, channel_name=None):
        """Formerly are_you_capping()"""
        if hasattr(self.bot, "voice") and channel_name:
            self.bot.voice.disconnect()
        message = ctx.message
        dest_channel = channel_name
        clip_chosen = song_id

        meme_list = glob.glob("micspam/*.*")
        if channel_name:
            try:
                voice_client = await self.bot.join_voice_channel(discord.Object(id=channel_name))
                if voice_client is None:
                    for server in self.bot.servers:
                        bound_voice_channel = discord.utils.get(server.channels, name=str(dest_channel))
                        if bound_voice_channel is None:
                            continue
                        voice_client = await self.bot.join_voice_channel(discord.Object(id=bound_voice_channel))
                        if voice_client is not None:
                            log.info("Micspam bound successfully to {.name}".format(bound_voice_channel))
                            break

            except Exception as e:
                log.exception("Error in micspam")
                await self.bot.say("Couldn't find that channel or already connected")
                return

        elif hasattr(self.bot, "voice"):
            pass

        l = list(self.bot.voice_clients)

        micspam = self.get_micspam(clip_chosen, meme_list)
        if l is None:
            await self.bot.send_message(message.channel, "Couldn't connect to the channel.")
            return
        elif micspam is not None:
            voice_connection = l[0]
            player = voice_connection.create_ffmpeg_player(micspam, after=lambda: self.micspam_after(voice_connection))
            player.start()
        else:
            await self.bot.send_message(message.channel, "That micspam value doesn't exist.")
            return

    @commands.command(hidden=True, pass_context=True, aliases=["spam"])
    async def capp(self, ctx, file: int, *, channel_name: str=None):
        """
        Micspam a certain channel
        :param ctx: Context
        :param channel_name: Voice channel name
        :param file: File (digit) found by %micspam
        :return: None
        """
        await self.play_micspam(ctx, file, channel_name)

    @commands.command(hidden=True, pass_context=True)
    async def grand_dad(self, ctx):
        """Fleenstones!?"""
        if ctx.message.author.voice is not None:
            await self.play_micspam(ctx.message.author.voice.voice_channel.name, 9, ctx)

    @commands.command(pass_context=True, hidden=True)
    async def micspam(self):
        meme_list = glob.glob("micspam/*.*")
        output_msg = ""
        for n, file in enumerate(meme_list):
            output_msg += "{0}: {1}\n".format(n, file)

        await self.bot.say(output_msg)


def setup(bot):
    bot.add_cog(Micspam(bot))
