import asyncio
import discord
import datetime
from discord.ext import commands
from .utils import checks
# import operator
# import math


"""
<bot>:activity                                              # NAMESPACE for app

<ns>:config                                                 # HASH for global defaults (used if guild default not set)
    cooldown_default                                        # Default cooldown duration
    pad_amount_default                                      # Default amount of message to pad new users
                                                            # 0 to disable
    score_period_default                                    # Default period for which messages count towards score
    prune_period_default                                    # Default period beyond which messages are pruned out of DB
    
<ns>:guilds                                                 # SET for IDs of guilds being watched

<ns>:guilds                                                 # NAMESPACE for guilds

<ns>:guilds:<guild_id>                                      # HASH for guild configuration
    cooldown                                                # Cooldown duration
    weight                                                  # Default weight
    pad_amount                                              # Number of messages new members will be padded with or
                                                            # 0 to disable
    score_period                                            # Number of days for which messages count towards score
    prune_period                                            # Number of days beyond which messages are pruned out of DB

<ns>:guilds:<guild_id>                                      # NAMESPACE for guild message records

<ns>:guilds:<guild_id>:cooldown                             # HASH for channel cooldowns

<ns>:guilds:<guild_id>:weights                              # HASH for channel weights

<ns>:guilds:<guild_id>:members                              # SET of members already logged from a guild

<ns>:guilds:<guild_id>:members                              # NAMESPACE for member records on a guild

<ns>:guilds:<guild_id>:members:<member_id>:<channel_id>     # ZSET to store message records. UNIX timestamp score
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

        # self._selected_guild = None
        # self._selected_channel = None

        self._config_slots = {
            'global': [
                'cooldown_default',
                'pad_amount_default',
                'score_period_default',
                'prune_period_default'
            ],
            'guild': [
                'cooldown',
                'weight',
                'pad_amount',
                'score_period',
                'prune_period',
            ],
            'channel': [
                'cooldown',
                'weight',
            ],
        }
        self._builtin_defaults = {
            'cooldown': 5,
            'score_period': 90,
            'prune_period': 365,
            'weight': 1,
            'pad_enabled': False,
            'pad_amount': 30
        }

    ####################################################################################################################
    # Get (and cache) DB records and configs
    ####################################################################################################################

    def _load_guild_member_cache_from_db(self):
        recorded_members = {}
        for guild in self.db.smembers(f'{self.ns}:guilds'):
            recorded_members[int(guild)] = set()
            for member in self.db.smembers(f'{self.ns}:guilds:{guild}:members'):
                recorded_members[int(guild)].add(int(member))
        return recorded_members

    def pad_enabled(self, guild_id):  # TODO: REMOVE AND USE PAD AMOUNT
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

    def get_pad_amount(self, guild_id):  # TODO: MAKE SURE IT'S INT. if '0' IS True. if 0 IS False.
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
        return int(pad_amount)

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

    ####################################################################################################################
    # Cooldown and cooldown check
    ####################################################################################################################

    async def put_cooldown(self, member_id, channel_id, dur):
        s = (member_id, channel_id)
        self.cooldown.add(s)
        await asyncio.sleep(int(dur))
        self.cooldown.remove(s)

    def check_cooldown(self, member, channel):
        if member.bot:
            return True
        # s = (member.id, channel.id)
        return (member.id, channel.id) in self.cooldown  # or member.id == self.bot.user.id

    def check(self, m):
        """Returns early if in DMs, not a watched guild,
        or if user/channel currently on cooldown"""
        if not isinstance(m.channel, discord.TextChannel):
            return True

        if m.guild.id not in self._guilds:
            return True

        return self.check_cooldown(m.author, m.channel)

    ####################################################################################################################
    # Normal processing
    ####################################################################################################################

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

    async def on_message_delete(self, m):
        if self.check(m):
            return

        guild, channel, member = m.guild, m.channel, m.author

        self.db.zrem(f'{self.ns}:guilds:{guild.id}:members:{member.id}:{channel.id}', str(m.id))

    def _pad(self, guild_id, member_id, ts):
        """Pads a new user's points with `pad_amount`
        message records even spaced across `score_period`
        days in a special `pad` namespace"""
        pad_amount, score_period = self.get_pad_amount(guild_id), self.get_score_period(guild_id)
        td = datetime.timedelta(seconds=((86400 * score_period) / pad_amount))
        self.db.zadd(f'{self.ns}:guilds:{guild_id}:members:{member_id}:pad',
                     **{str((pad_amount - i)): str((ts - (td * i)).timestamp()) for i in range(pad_amount)})

    ####################################################################################################################
    # Subroutines
    ####################################################################################################################

    def color(self, name: str="blurple"):
        """Helper function to get discord.Colour color."""
        return getattr(discord.Colour, name)()

    def msg(self, *, title: str=None, msg: str, level=0):
        """Sends a notification message for command completion"""
        color = ['blue', 'orange', 'red']
        icon = ["ℹ", "⚠", "⛔"]
        return discord.Embed(title=title, description=f"{icon[level]}  {msg}", color=self.color(color[level]))

    def table_space_formatting(self, slots, **values):
        # db = self.db.hgetall(key)  # TODO: Handle the db getting outside of here
        spaced = [f"{i}{' ' * (max(map(len, slots)) - len(i))}" for i in slots]
        return "\n".join([f"{spaced[i]} : {values.get(slots[i], 'Not Defined')}" for i in range(len(slots))])

    def get_config(self, scope, key, name=None):
        slots = self._config_slots[scope]
        name = f" for: {name}" if name else ""
        emb = discord.Embed(title=f"{scope.capitalize()} Configs{name}",
                            description=f"```\n{self.config_format(slots, key)}\n```\nUse `config"
                                        f" set` to change a configuration.",
                            color=self.color('dark_grey'))
        return emb

    def get_channel_config(self):
        pass

    ####################################################################################################################
    # Configuration commands
    ####################################################################################################################

    @commands.group(name='activity', aliases=['metrics'], invoke_without_command=True)
    async def activity(self, ctx):
        """A system to guage activity levels of users and channels

        See help page for subcommands for more details"""
        await self.bot.formatter.format_help_for(ctx, ctx.command)

    ####################################################################################################################
    # Global config
    ####################################################################################################################

    @checks.sudo()
    @activity.group(name='config', invoke_without_command=True)
    async def a_config(self, ctx):
        """Set and view global default configurations

        These configurations will be used if guild/channel
        specific configurations are not specified.

        Use this command without `set` subcommand to
        view all current global defaults"""
        await ctx.send(embed=self.get_config('global', f"{self.ns}:config"))

    @checks.sudo()
    @a_config.group(name='set', invoke_without_command=True)
    async def a_set(self, ctx, key: str, value: int):
        """Set a global default configuration

        Available values to set are:
        ```
        cooldown_default
        pad_amount_default
        score_period_default
        prune_period_default
        ```"""
        pass  # Set a global default config

    ####################################################################################################################
    # Guild config
    ####################################################################################################################

    @activity.group(name='guild', invoke_without_command=True)
    async def a_guild(self, ctx):
        """Manage tracked guilds

        Available values to set are:
        ```
        cooldown
        weight
        pad_amount
        score_period
        prune_period
        ```"""
        await ctx.send(embed=self.get_config('guild', f"{self.ns}:guilds:{ctx.guild.id}", ctx.guild.name))

    @a_guild.command(name='enable')
    async def g_enable(self, ctx):
        """Enable Activity Monitor on a guild"""
        if ctx.guild.id in self._guilds:
            em = self.msg(msg=f"Activity monitor already active on guild {ctx.guild.name}", level=1)
        else:
            self._guilds.add(ctx.guild.id)
            self.db.sadd(f'{self.ns}:guilds', ctx.guild.id)
            em = self.msg(msg=f"Activity monitor active on guild {ctx.guild.name}")
        await ctx.send(embed=em)

    @a_guild.command(name='disable')
    async def g_disable(self, ctx):
        """Disable Activity Monitor on a guild"""
        if ctx.guild.id in self._guilds:
            self._guilds.remove(ctx.guild.id)
            self.db.srem(f'{self.ns}:guilds', str(ctx.guild.id))
            em = self.msg(msg=f"Activity monitor disabled on guild {ctx.guild.name}")
        else:
            em = self.msg(msg=f"Activity monitor not active on guild {ctx.guild.name}", level=1)
        await ctx.send(embed=em)

    @a_guild.group(name='config', invoke_without_command=True)
    async def g_config(self, ctx):
        await ctx.send(embed=self.get_config('guild', f"{self.ns}:guilds:{ctx.guild.id}", ctx.guild.name))

    @g_config.group(name='set', invoke_without_command=True)
    async def g_set(self, ctx, key: str, value: int):
        pass  # Set a guild config

    ####################################################################################################################
    # Channel config
    ####################################################################################################################

    @activity.group(name='channel')
    async def a_channel(self, ctx):
        pass

    @a_channel.group(name='config', invoke_without_command=True)
    async def c_config(self, ctx, *, channel: discord.TextChannel):
        pass

    @a_channel.command(name='set')
    async def c_set(self, ctx, key: str, value: int):
        pass


def setup(bot):
    bot.add_cog(ActivityMonitor(bot))
