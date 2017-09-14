import asyncio
import discord
# import operator
# import math
import datetime
from discord.ext import commands


"""
<bot>:activity                                              # NAMESPACE for app

<bot>:activity:config                                       # HASH for global defaults (used if guild default not set)
    cooldown_default                                        # Default cooldown duration
    pad_amount_default                                      # Default amount of message to pad new users
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

<bot>:activity:guilds:<guild_id>:members                    # NAMESPACE for member records on a guild

<bot>:activity:guilds:<guild_id>:members:<member_id>:<channel_id>  # ZSET to store message records. UNIX timestamp score
                                                            # with message snowflake as value
"""


class ActivityMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.ns = f"{self.bot.app_name}:activity"

        self.cooldown = set()

        self._pad_enabled = {}
        self._pad_channel = {}
        self._pad_amount = {}
        self._cooldown_duration = {}
        self._score_period = {}

        self._recorded_members = self._load_guild_member_cache_from_db()
        self._guilds = set([int(i) for i in self.db.smembers(f'{self.ns}:guilds')])

        self._builtin_defaults = {
            'cooldown': 5,
            'score_period': 90,
            'prune_period': 365,
            'weight': 1,
            'pad_enabled': False,
            'pad_amount': 30
        }

    # Get (and cache) DB records and configs

    def _load_guild_member_cache_from_db(self):
        recorded_members = {}
        for guild in self.db.smembers(f'{self.ns}:guilds'):
            recorded_members[int(guild)] = set()
            for member in self.db.smembers(f'{self.ns}:guilds:{guild}:members'):
                recorded_members[int(guild)].add(int(member))
        return recorded_members

    def pad_enabled(self, guild_id):
        try:
            pad_enabled = self._pad_enabled[guild_id]
        except KeyError:
            pad_enabled = self.db.hget(f'{self.ns}:guilds:{guild_id}', 'pad_enabled')
            if pad_enabled:
                self._pad_enabled[guild_id] = True
            else:
                self._pad_enabled[guild_id] = False
                pad_enabled = False
        return pad_enabled

    def get_pad_amount(self, guild_id):
        try:
            pad_amount = self._pad_amount[guild_id]
        except KeyError:
            pad_amount = self.db.hget(f'{self.ns}:guilds:{guild_id}', 'pad_amount')
            if pad_amount:
                self._pad_amount[guild_id] = int(pad_amount)
            else:
                pad_amount = self.db.hget(f'{self.ns}:config', 'pad_amount')
                if pad_amount:
                    self._pad_amount[guild_id] = int(pad_amount)
                else:
                    pad_amount = self._builtin_defaults['pad_amount']
                    self._pad_amount[guild_id] = pad_amount
        return pad_amount

    def get_cooldown_dur(self, guild_id, channel_id):
        """Returns cooldown duration for a channel.
        In order, will check guild preference,
        guild default preference, built in default."""
        try:
            cooldown_duration = self._cooldown_duration[channel_id]
        except KeyError:
            cooldown_duration = self.db.hget(f'{self.ns}:guilds:{guild_id}:cooldown', f'{channel_id}')
            if cooldown_duration:
                self._cooldown_duration[channel_id] = int(cooldown_duration)
            else:
                cooldown_duration = self.db.hget(f'{self.ns}:guilds:{guild_id}', 'cooldown')
                if cooldown_duration:
                    self._cooldown_duration[channel_id] = int(cooldown_duration)
                else:
                    cooldown_duration = self.db.hget(f'{self.ns}:config', 'cooldown_default')
                    if cooldown_duration:
                        cooldown_duration = int(cooldown_duration)
                        self._cooldown_duration[channel_id] = cooldown_duration
                    else:
                        cooldown_duration = self._builtin_defaults['cooldown']
                        self._cooldown_duration[channel_id] = cooldown_duration
        return cooldown_duration

    def get_score_period(self, guild_id):
        try:
            score_period = self._score_period[guild_id]
        except KeyError:
            score_period = self.db.hget(f'{self.ns}:guilds:{guild_id}', 'score_period')
            if score_period:
                self._score_period[guild_id] = score_period
            else:
                score_period = self.db.hget(f'{self.ns}:config', 'score_period_default')
                if score_period:
                    self._score_period[guild_id] = score_period
                else:
                    score_period = self._builtin_defaults['score_period']
                    self._score_period[guild_id] = score_period
        return score_period

    def check_new_member(self, guild_id, member_id):
        """Check if a member has been recorded before."""
        if guild_id not in self._recorded_members.keys():
            self._recorded_members[guild_id] = set()

        if member_id in self._recorded_members[guild_id]:
            return False
        else:
            self._recorded_members[guild_id].add(member_id)
            self.db.sadd(f"{self.ns}:guilds:{guild_id}:members", str(member_id))
            return True

    # def get_current_guild_config(self, guild_id):
    #     """Get all current configuration options for a guild."""
    #     pass  # TODO: IS THIS REALLY NEEDED?

    # Set and check cooldown

    async def put_cooldown(self, member_id, channel_id, dur):
        s = (member_id, channel_id)
        self.cooldown.add(s)
        await asyncio.sleep(int(dur))
        self.cooldown.remove(s)

    def check_cooldown(self, member, channel):
        if member.bot:
            return True
        # s = (member.id, channel.id)
        return (member.id, channel.id) in self.cooldown  #  or member.id == self.bot.user.id

    def check(self, m):
        """Returns early if in DMs, not a watched guild,
        or if user/channel currently on cooldown"""
        if not isinstance(m.channel, discord.TextChannel):
            return True

        if m.guild.id not in self._guilds:
            return True

        return self.check_cooldown(m.author, m.channel)

    # Normal processing

    async def on_message(self, m):
        # Looks like ctx.created_at.timestamp() is datetime.datetime.utcnow()
        if self.check(m):
            return

        guild, channel, member, ts = m.guild, m.channel, m.author, m.created_at

        if self.pad_enabled(guild.id) and self.check_new_member(guild.id, member.id):
            self._pad(guild.id, member.id, ts)
        self.db.zadd(f'{self.ns}:guilds:{guild.id}:members:{member.id}:{channel.id}', ts.timestamp(), m.id)

        # self.bot.loop.create_task(self.put_cooldown(member, channel))
        await self.put_cooldown(member.id, channel.id, self.get_cooldown_dur(guild, channel))

    async def on_message_delete(self, m):  # TODO: DELETE MESSAGE RECORD IF IT EXISTS
        pass

    async def on_member_remove(self, m):  # TODO: DELETE ACTIVITY RECORDS OR NAH?
        pass

    def _pad(self, guild_id, member_id, ts):
        pad_amount, score_period = self.get_pad_amount(guild_id), self.get_score_period(guild_id)
        td = datetime.timedelta(seconds=((86400 * score_period) / pad_amount))
        self.db.zadd(f'{self.ns}:guilds:{guild_id}:members:{member_id}:pad',
                     **{str((pad_amount - i)): str((ts - (td * i)).timestamp()) for i in range(pad_amount)})

    # Configuration commands

    @commands.group(name='metrics', hidden=True)
    async def metrics(self, ctx):
        pass

    @metrics.command(name='addguild', hidden=True)
    async def addguild(self, ctx, *, guild: int=None):
        if not guild:
            guild = ctx.guild.id
        if self.db.sismember(f'{self.ns}:guilds', guild):
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
                self.db.sadd(f'{self.ns}:guilds', guild)
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

        channels = self.db.smembers(f'{self.ns}:{guild}:channels')
        users = self.db.smembers(f'{self.ns}:{guild}:users')

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

    @metrics.group(name='set', hidden=True)
    async def m_set(self, ctx):
        pass

    @m_set.command(name='pad')  # TODO: CONFIGURE PAD OPTIONS
    async def pad(self, ctx, messages: int=None, channel: discord.TextChannel=None, *, guild: discord.Guild=None):
        return

    # @commands.command()
    # async def tempfix(self, ctx):
    #     for channel in ctx.guild.channels:
    #         self.db.sadd(f'{self.ns}:{ctx.guild.id}:channels', channel.id)
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
