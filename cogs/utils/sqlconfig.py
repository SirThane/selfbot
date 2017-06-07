"""I guess I'm gonna try to make Danny's config.py, but for SQLite3.

No idea how this is gonna work."""

import discord
import sqlite3

class SQLConfig:

    def __init__(self, filename, *columns):
        self.filename = filename
        self.columns = columns


def setup(bot):
    bot.add_cog(SQLConfig(bot))