"""Custom notifications"""

import discord
from discord.ext import commands
from datetime import datetime
import pytz
import logging
import asyncio


log = logging.getLogger()
green = 0x00FF00
red = 0xFF0000
tz = pytz.timezone('America/Kentucky/Louisville')


async def resp(ctx, title, message, color: int, delete=True):
    embed = discord.Embed(title=f'Notifications: {title}', description=message, color=color)
    await ctx.message.delete()
    msg = await ctx.send(embed=embed)
    if delete:
        await asyncio.sleep(5)
        await msg.delete()


class Notifications:
    """Handler for custom notifications

    Intended for selfbots.
    Uses Redis DB.
    Replace with your external storage.
    Works in tandem with another bot.
    Will call [p]notif"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.dbkey = f'{self.bot.app_name}:notifs'  # I'm cheating. Gonna do them all this way. "selfbot:notifs"
        if not self.update_channel():
            log.warning('Notification channel could not be set')
        if not self.update_watched():
            log.info('Notifications cogs loaded. Watch list empty.')

    @property
    def watched(self):
        return [i for i in self._watched]

    def update_channel(self, channel_id: int=None):
        if channel_id:
            channel = self.bot.get_channel(id=channel_id)
            if channel:
                self.db.hset(f'{self.dbkey}:config', 'channel', channel_id)
                self.channel = channel
                return True
            else:
                return False
        else:
            channel_id = self.db.hget(f'{self.dbkey}:config', 'channel')
            if channel_id is not None:
                channel = self.bot.get_channel(id=int(channel_id))
                if channel:
                    self.channel = channel
                    return True
                else:
                    return False
            else:
                return False

    def update_watched(self, phrase: str=None, add: bool=False):
        if phrase:
            if add:
                ret = self.db.sadd(f'{self.dbkey}:watched', phrase)
                if ret:
                    self._watched = list(self.db.smembers(f'{self.dbkey}:watched'))
                    return True  # item added
                else:
                    return False  # item already in DB
            else:
                ret = self.db.srem(f'{self.dbkey}:watched', phrase)
                if ret:
                    self._watched = list(self.db.smembers(f'{self.dbkey}:watched'))
                    return True  # item removed
                else:
                    return False  # item not in DB
        else:
            self._watched = list(self.db.smembers(f'{self.dbkey}:watched'))
            if len(self._watched) > 0:
                return True  # watch list updated
            else:
                return False  # watch list empty

    @commands.group(name='notifs')
    async def notifs(self, ctx):
        """Configure self notifications"""
        pass

    @notifs.command(name='update_channel', aliases=['channel'], pass_context=True)
    async def _update_channel(self, ctx, channel_obj: discord.TextChannel=None):
        try:
            if channel_obj:
                if self.update_channel(channel_obj.id):
                    await resp(ctx, 'Channel Update', 'Channel updated successfully.', green)
                else:
                    await resp(ctx, 'Channel Update', 'Failed to set new notification channel.', red)
            else:
                if self.update_channel():
                    await resp(ctx, 'Channel Reload', 'Channel reloaded from DB successfully.', green)
                else:
                    await resp(ctx, 'Channel Reload', 'Failed to reload channel from DB.', red)
        except Exception as e:
            await print(f'{type(e).__name__}: {str(e)}')

    @notifs.group(name='phrase')
    async def phrase(self, ctx):
        pass

    @phrase.command(name='list')
    async def _list(self, ctx):
        self.update_watched()
        l = '\n'.join(self._watched)
        if l == '':
            l = 'No phrases are currently being watched.'
        await resp(ctx, 'Watched Phrases', l, green)

    @phrase.command(name='add_phrase', aliases=['add_word', 'add'], pass_context=True)
    async def add_phrase(self, ctx, *, phrase: str):
        if self.update_watched(phrase.lower(), add=True):
            await resp(ctx, 'Add Phrase', 'Phrase successfully added to list.', green)
        else:
            await resp(ctx, 'Add Phrase', 'Phrase already in list.', red)

    @phrase.command(name='del_phrase', aliases=['del_word', 'del', 'rem'], pass_context=True)
    async def del_phrase(self, ctx, *, phrase: str):
        if self.update_watched(phrase.lower(), add=False):
            await resp(ctx, 'Remove Phrase', 'Phrase successfully removed from list.', green)
        else:
            await resp(ctx, 'Remove Phrase', 'Phrase not in list.', red)

    async def action_on_message(self, message):
        if hasattr(self, 'channel') and message.author.id != self.bot.user.id\
                and isinstance(message.channel, discord.TextChannel):
            l = self.watched
            l.append(message.guild.me.display_name.lower())
            if any(map(lambda x: x in message.content.lower(), l)):
                author = message.author
                timestamp = tz.localize(datetime.now()).strftime("%b. %d, %Y %I:%M %p")
                display_name = f' ({author.display_name})' if author.display_name != author.name else ''
                em = discord.Embed(title='{0.guild}: #{0.channel} at {1}'.format(message, timestamp),
                                   description=message.content, color=author.color)
                em.set_author(name='{0.name}#{0.discriminator}{1}'.format(author, display_name),
                              icon_url=author.avatar_url_as(format='png'))
                try:
                    await self.channel.send(f'$notif \
                    {message.guild.name}: {message.channel.name}\n<#{message.channel.id}>', embed=em)
                except AttributeError:
                    log.warning('Channel not set: {}'.format(self.db.hget(f'{self.dbkey}:config', 'channel')))

    async def on_message(self, message):
        await self.action_on_message(message)

    async def on_message_edit(self, before, after):
        await self.action_on_message(after)

def setup(bot):
    bot.add_cog(Notifications(bot))
