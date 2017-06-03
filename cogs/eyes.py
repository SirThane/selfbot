""":eyes:"""

from discord.ext import commands
import discord
import aiohttp
import random
import asyncio


rating_colors = {
    "s": discord.Color.green(),
    "q": discord.Color.orange(),
    "e": discord.Color.red()
}


class E621:

    USER_AGENT = "Discord bot by lucaholic"

    @staticmethod
    async def _fetch(client, tags):
        """
        Get a random image from e6.
        :param client: aiohttp client
        :param tags: List of desired tags.
        :return: URL to an image.
        """

        extra_tags = ["order:random", "rating:e"]

        tags += extra_tags

        if ["rating:s", "rating:q"] in tags:  # Allow for sfw stuff
            tags.remove("rating:e")

        print(tags)

        params = {"limit": "1", "tags": " ".join(tags)}
        async with client.get("https://e621.net/post/index.json", params=params) as resp:
            if resp.status not in [200, 400]:
                raise aiohttp.HttpBadRequest("Request failed: " + str(resp.status))

            return await resp.json()

    @staticmethod
    async def get_image(tags):
        async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as client:
            return await E621._fetch(client, tags)


class Eyes:

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @staticmethod
    def _format_list(items: list):
        """Dealing with lists and commas."""
        output = ""
        for num, item in enumerate(items):
            output += item
            output += ", " if (num + 1 != len(items)) else ""

        return output

    def _create_embed(self, image):
        artists = self._format_list(image["artist"])
        embed = discord.Embed(color=rating_colors[image["rating"]],
                              title="#{0}: {1}".format(image["creator_id"], artists),
                              description="Score: {score}\nFavorites: {fav_count}".format(**image))

        embed = embed.set_image(url=image["file_url"])
        embed.set_footer(text="https://e621.net/post/show/{}".format(image["id"]))

        return embed

    @commands.command(hidden=True, pass_context=True)
    async def e6(self, ctx, *, tags: str):
        """
        Pull an image from e621.
        tags: space-separated tags
        """
        try:
            response = await E621.get_image(tags.split())  # Response returns a list of dicts
        except aiohttp.HttpBadRequest as e:
            await self.bot.edit_message(ctx.message, e)
            return

        if isinstance(response, dict) and not response["success"]:  # Failed
            if response["reason"] == "You can only search up to 6 tags at once":  # Base tags cause issues

                await self.bot.edit_message(ctx.message, "Error: You can only search up to 4 tags at once.")  # Because we already use 2

            else:
                await self.bot.edit_message(ctx.message, "Error: {}.".format(response["reason"]))

        elif len(response) < 1:
            print(response)
            await self.bot.edit_message(ctx.message, "No results found.")
            return
        chosen_image = random.choice(response)
        embed = self._create_embed(chosen_image)

        await self.bot.edit_message(ctx.message, "", embed=embed)


def setup(bot):
    bot.add_cog(Eyes(bot))

if __name__ == "__main__":
    tag_query = input("Tags?")
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(E621.get_image(tag_query.split())))
