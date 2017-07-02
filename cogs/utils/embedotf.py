"""So, this is going to be a helper for creating embeds.

Or something"""

import discord

default = {
    "embed": {
        "title": "undefined",
        "description": "undefined",
        "color": 0x000000
    },
    "set_author": {
        "name": "undefined",
        "url": "strurl",
        "icon_url": "strurl"
    },
    "set_footer": {
        "text": "undefined",
        "icon_url": "strurl"
    },
    "set_thumbnail": {
        "url": "strurl"
        },
    "add_field": [
        {
            "name": "str",
            "value": "str",
            "inline": bool
        },
        {
            "name": "str",
            "value": "str",
            "inline": bool
        },
        {
            "name": "str",
            "value": "str",
            "inline": bool
        }
    ]
}


class EmbedOTF:

    def __init__(self):
        pass
