from .streams import Streams


async def setup(bot):
    cog = Streams(bot)
    await cog.initialize()
    bot.add_cog(cog)
