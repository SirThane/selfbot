import re
import discord
import time
from discord.ext import commands


def extract_mentions(text, message):
    """Extract mentions in text and replace them with usernames"""
    mentions_found = re.findall(r'(<@!?\d{17,18}>)', text)  # Extract mentions from the input
    ids_found = re.findall(r'(\d{17,18})', text)  # Extract mentions from the input, but get the IDs.
    if len(mentions_found) == 0:
        return text
    else:
        for num, mention in enumerate(mentions_found):
            member_mentioned = discord.utils.get(message.server.members, id=ids_found[num])
            if member_mentioned is not None:
                text = text.replace(mention, member_mentioned.name)  # Assigning it to the str.replace was crucial here
            else:
                text = text.replace(mention, "[somebody]")
        return text


def check_ids(text):
    """Check for IDs"""
    id_found = re.search(r'(\d{17,18})', text)
    if id_found and id_found.group(0) is not None:
        return True
    else:
        return False


def check_mentions(text):
    """
    Check message for mentions
    :param text: Input
    :return: True if mention found, otherwise False
    """
    mention_found = re.search(r'(<@!?\d{17,18}>)', text)
    if mention_found is not None and mention_found.group(0) is not None:
        return True
    else:
        return False


def check_urls(text):
    """
    Check message for urls
    :param text: Input
    :return: True if link found, otherwise False
    """
    link_found = re.search(
        r'(https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&/=]*))', text)
    if link_found is not None and link_found.group(0) is not None:
        return True
    else:
        return False


def check_input(text):
    """
    Check text for certain components which we don't really want to end up in messages, such as mentions or urls.
    Does not do any actual parsing.
    :param text: String to check.
    :return: True if mention or link is found, otherwise false.
    """

    return check_mentions(text) or check_urls(text)


def get_timestamp():
    now = time.localtime()
    return time.strftime("%a %b %d, %Y at %H:%M %Z", now)


def format_embed(embed, member):
    """Do basic formatting on the embed"""
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name="User ID", value=member.id)
    embed.set_footer(text=get_timestamp())
    return embed


class UserType:

    def __init__(self, argument):

        if isinstance(argument, discord.Member):
            self.user_id = argument.id
        elif check_ids(argument):
            self.user_id = argument
        else:
            raise commands.BadArgument("User not found.")


# More stuff from robodanny, because it's honestly a really elegant way of doing what I wanted to otherwise do
