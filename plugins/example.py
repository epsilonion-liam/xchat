from nextcord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Example cog initialized")

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello from the example cog!')

def setup(bot):
    """Setup function for the cog"""
    if bot is None:
        logger.error("Bot object is None in setup function")
        return
    
    try:
        logger.info("Adding Example cog to bot")
        bot.add_cog(Example(bot))
        logger.info("Example cog added successfully")
    except Exception as e:
        logger.error(f"Error adding Example cog: {e}")
