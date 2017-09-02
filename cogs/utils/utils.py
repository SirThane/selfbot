import re
import discord
import time
import redis
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


# class UserType:  # Just cast function args as discord.Member
#
#     def __init__(self, argument):
#
#         if isinstance(argument, discord.Member):
#             self.user_id = argument.id
#         elif check_ids(argument):
#             self.user_id = argument
#         else:
#             raise commands.BadArgument("User not found.")


class Paginator:

    def __init__(self, page_limit=1000, trunc_limit=2000):
        self.page_limit = page_limit
        self.trunc_limit = trunc_limit

    def paginate(self, value):
        """
        To paginate a string into a list of strings under
        `self.page_limit` characters. Total len of strings
        will not exceed `self.trunc_limit`.
        :param value: string to paginate
        :return list: list of strings under 'page_limit' chars
        """
        spl = str(value).split('\n')
        ret = []
        page = ''
        total = 0
        for i in spl:
            if total + len(page) < self.trunc_limit:
                if (len(page) + len(i)) < self.page_limit:
                    page += '\n{}'.format(i)
                else:
                    if page:
                        total += len(page)
                        ret.append(page)
                    if len(i) > (self.page_limit - 1):
                        tmp = i
                        while len(tmp) > (self.page_limit - 1):
                            if total + len(tmp) < self.trunc_limit:
                                total += len(tmp[:self.page_limit])
                                ret.append(tmp[:self.page_limit])
                                tmp = tmp[self.page_limit:]
                            else:
                                ret.append(tmp[:self.trunc_limit - total])
                                break
                        else:
                            page = tmp
                    else:
                        page = i
            else:
                ret.append(page[:self.trunc_limit - total])
                break
        else:
            ret.append(page)
        return ret


def bool_str(arg):
    if arg == 'True':
        return True
    elif arg == 'False':
        return False
    else:
        return arg


def bool_transform(arg):
    if isinstance(arg, str):
        return bool_str(arg)
    elif isinstance(arg, list):
        for i in range(len(arg)):
            arg[i] = bool_str(arg[i])
        return arg
    elif isinstance(arg, dict):
        for i in arg.keys():
            arg[i] = bool_str(arg[i])
        return arg


class StrictRedis(redis.StrictRedis):
    """Turns 'True' and 'False' values returns
    in redis to bool values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret
