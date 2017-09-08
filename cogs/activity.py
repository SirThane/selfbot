import asyncio
import discord
# import operator
# import math
# import datetime
from discord.ext import commands


"""
<bot>:activity                                              # NAMESPACE for app

<bot>:activity:config                                       # HASH for global defaults (used if guild default not set)
    cooldown_default                                        # Default cooldown duration
    score_period_default                                    # Default period for which messages count towards score
    prune_period_default                                    # Default period beyond which messages are pruned out of DB
    
<bot>:activity:guilds                                       # SET for IDs of guilds being watched

<bot>:activity:guilds                                       # NAMESPACE for guilds

<bot>:activity:guilds:<guild_id>                            # HASH for guild configuration
    cooldown                                                # Cooldown duration
    pad_enabled                                             # State of padding
    pad_channel                                             # ID of channel padding messages are recorded under
    pad_amount                                              # Number of messages new members will be padded with
    score_period                                            # Number of days for which messages count towards score
    prune_period                                            # Number of days beyond which messages are pruned out of DB

<bot>:activity:guilds:<guild_id>                            # NAMESPACE for guild message records

<bot>:activity:guilds:<guild_id>:cooldown                   # HASH for channel specific cooldowns

<bot>:activity:guilds:<guild_id>:weights                    # HASH for channel weights

<bot>:activity:guilds:<guild_id>:members                    # SET of members already logged from a guild

<bot>:activity:guilds:<guild_id>:<member_id>:<channel_id>   # ZSET to store message records. UNIX timestamp score with
                                                            # message snowflake as value
"""


class ActivityMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.db_key = f"{self.bot.app_name}:activity"

        self.cooldown = set()

        self._pad_enabled = {}
        self._pad_channel = {}
        self._pad_amount = {}
        self._cooldown_duration = {}
        self._builtin_defaults = {
            'cooldown': 5,
            'score_period': 90,
            'prune_period': 365,
            'weight': 1,
        }

    # Get (and cache) DB records

    def pad_enabled(self, guild_id):
        try:
            pad_enabled = self._pad_enabled[guild_id]
        except KeyError:
            pad_enabled = self.db.hget(f'{self.db_key}:guilds:{guild_id}', 'pad_enabled')
            if pad_enabled:
                self._pad_enabled[guild_id] = True
            else:
                self._pad_enabled[guild_id] = False
                pad_enabled = False
        return pad_enabled

    def get_cooldown_dur(self, guild_id, channel_id):
        """Returns cooldown duration for a channel.
        In order, will check guild preference,
        guild default preference, built in default."""
        try:
            cooldown_duration = self._cooldown_duration[channel_id]
        except KeyError:
            cooldown_duration = self.db.hget(f'{self.db_key}:guilds:{guild_id}:cooldown', f'{channel_id}')
            if cooldown_duration:
                self._cooldown_duration[channel_id] = int(cooldown_duration)
            else:  # TODO: CHECK GUILD DEFAULT BEFORE GLOBAL DEFAULT
                cooldown_duration = self.db.hget(f'{self.db_key}:config', 'default_cooldown')
                if cooldown_duration:
                    cooldown_duration = int(cooldown_duration)
                    self._cooldown_duration[channel_id] = cooldown_duration
                else:
                    cooldown_duration = self._builtin_defaults['cooldown']
                    self._cooldown_duration[channel_id] = cooldown_duration
        return cooldown_duration

    def check_member(self, guild_id, member_id):
        pass

    # Set and check cooldown

    async def put_cooldown(self, member, channel, dur):
        s = (member.id, channel.id)
        self.cooldown.add(s)
        await asyncio.sleep(int(dur))
        self.cooldown.remove(s)

    def check_cooldown(self, member, channel):
        if member.bot:
            return True
        s = (member.id, channel.id)
        return s in self.cooldown or member.id == self.bot.user.id

    def check(self, m):
        """Returns early if in DMs, not a watched guild,
        or if user/channel currently on cooldown"""
        if isinstance(m.channel, discord.TextChannel):
            return False

        if not self.db.sismember(f'{self.db_key}:guilds', str(m.guild.id)):
            return True

        return self.check_cooldown(m.author, m.channel)

    # On Message

    async def on_message(self, m):
        # Looks like ctx.created_at.timestamp() is datetime.datetime.utcnow()
        if self.check(m):
            return

        guild, channel, member, ts = m.guild, m.channel, m.author, m.created_at.timestamp()

        if self.pad_enabled(guild.id):
            self._pad(guild.id, member.id)
        self.db.zadd(f'{self.db_key}:guilds:{guild.id}:{member.id}:{channel.id}', ts, m.id)

        # self.bot.loop.create_task(self.put_cooldown(member, channel))
        await self.put_cooldown(member, channel, self.get_cooldown_dur(guild, channel))

    def _pad(self, guild_id, member_id):
        pass

    # Configuration commands

    @commands.group(name='metrics', hidden=True)
    async def metrics(self, ctx):
        pass

    @metrics.command(name='addguild', hidden=True)
    async def addguild(self, ctx, *, guild: int=None):
        if not guild:
            guild = ctx.guild.id
        if self.db.sismember(f'{self.db_key}:guilds', guild):
            g = self.bot.get_guild(id=guild)
            em = discord.Embed(title="User Metrics",
                               description=f"Activity monitor already active on guild {g.name}",
                               color=discord.Colour.red())
            resp = await ctx.send(embed=em)
            await asyncio.sleep(5)
            await resp.delete()
        else:
            g = self.bot.get_guild(id=guild)
            if g:
                self.db.sadd(f'{self.db_key}:guilds', guild)
                em = discord.Embed(title="User Metrics",
                                   description=f"Activity monitor active on guild {g.name}",
                                   color=discord.Colour.green())
                resp = await ctx.send(embed=em)
                await asyncio.sleep(5)
                await resp.delete()

    @metrics.command(name='get_report', hidden=True)
    async def get_report(self, ctx, guild=None):
        # TODO: Refactor the shit out of this before it ever gets off the ground
        if not guild:
            guild = ctx.guild

        channels = self.db.smembers(f'{self.db_key}:{guild}:channels')
        users = self.db.smembers(f'{self.db_key}:{guild}:users')

        c = {}
        for channel in channels:
            c[channel] = self.bot.get_channel(id=int(channel))

        u = {}
        for user in users:
            u[user] = self.bot.get_member(id=int(user))

        with open('test.txt', 'w') as out:
            out.write(f'For guild: {guild.name}')
            for user, user_id in u.items():
                member = self.bot.get_member(id=int(user))
                out.write(f'User: {member.name}#{member.discriminator}')
                # for channel in channels:
                #     pass

    @metrics.group(name='set_pad', hidden=True)
    async def _set(self, ctx):
        pass

    @_set.command(name='pad')
    async def pad(self, ctx, messages: int=None, channel: discord.TextChannel=None, *, guild: discord.Guild=None):
        return

    # @commands.command()
    # async def tempfix(self, ctx):
    #     for channel in ctx.guild.channels:
    #         self.db.sadd(f'{self.db_key}:{ctx.guild.id}:channels', channel.id)
    #         await ctx.message.delete()

    # Kept for reference  # TODO: REMOVE

# ranks = {
#     10: [1, "Beginner"],
#     69: [2, "Memer Rank 1"],
#     300: [3, "Talker"],
#     360: [4, "MLG'er"],
#     420: [5, "Memer Rank 2"],
#     666: [6, "Devil"],
#     1000: [7, "Active"],
#     1337: [8, "1337"],
#     3000: [9, "Really Active"],
#     6000: [10, "Extremely Active"],
#     9001: [11, "Memer Rank 3"],
#     10000: [12, "Too Active"]
# overrides = set()

    # def next_ranks(self, num):
    #     e = []
    #     for rank in ranks.keys():
    #         if int(rank) > int(num):
    #             e.append(ranks[rank][1])
    #     if len(e) == 0:
    #         e = ["Nothing left to do!!!"]
    #     return e

    # def next_rank(self, num):
    #     for i in range(100000):
    #         try:
    #             if ranks[num + i]:
    #                 return [ranks[num + i], num + i]
    #         except:
    #             continue
    #
    #     return [[69, "Nothing"], 10000]

    # @commands.command(name='rank', hidden=True, disabled=True)
    # async def rank(self, ctx, user: discord.Member=None):
    #     """Get someones rank"""
    #     if user is None:
    #         user = ctx.author
    #     d = self.db.hget('rankcount', user.id)
    #     if d is None:
    #         em = discord.Embed(title="No Data", description="Try get them to speak a little more!!!")
    #         await ctx.send(embed=em)
    #     else:
    #         em = discord.Embed(title=f"{str(user)}'s info")
    #         em.set_thumbnail(url=user.avatar_url)
    #         em.add_field(name="PyPoint count", value=f"{d} PyPoints")
    #         em.add_field(name="Current Rank", value=self.db.hget('currank', user.id))
    #         y = self.next_rank(int(d))
    #         prcnt = 'nil'  # math.floor((int(d) / int(y[1])) * 100)
    #         if y[0][0] == 69:
    #             em.add_field(name="Next Rank", value=f"Nothing left to do")
    #         else:
    #             em.add_field(name="Next Rank", value=f"Level {y[0][0]} - {y[0][1]}, {str(d)}/{y[1]} ({prcnt}%) there")
    #
    #         await ctx.send(embed=em)

    # @commands.command(name='leaderboard', hidden=True, disabled=True)
    # async def leaderboard(self, ctx):
    #     """Get the rank leaderboard"""
    #     em = discord.Embed(title="Please wait", description="Compiling sources and generating leaderboard...")
    #     message = await ctx.send(embed=em)
    #     lb = self.db.hgetall("rankcount")
    #     lb = {k: int(v) for k, v in lb.items()}
    #     lb = sorted(lb.items(), key=operator.itemgetter(1), reverse=True)
    #     _message = ""
    #     for i in range(0, 10):
    #         user = await self.bot.get_user_info(int(lb[i][0]))
    #         currank = self.db.hget("currank", str(user.id))
    #         _message += f"{i + 1}. {str(user)} - {lb[i][1]} PyPoints - Current Rank: {currank}\n"
    #     await message.delete()
    #     em = discord.Embed(title="Rank leaderboard", description=_message)
    #     await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(ActivityMonitor(bot))
