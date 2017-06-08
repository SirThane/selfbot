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

# db = sqlite3.connect('dbase.db')
# c = db.cursor()
#
# # c.execute("""CREATE TABLE playground (
# #                 val1 text,
# #                 val2 text,
# #                 val3 integer
# #                 )""")
#
# c.execute("""INSERT INTO playground VALUES
#             ('Test', 'Text', 42)""")
#
# db.close()