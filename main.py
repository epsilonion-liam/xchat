import os
import logging
import sys
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents for the bot
intents = nextcord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True  # Needed for member-related features

# Initialize bot
bot = commands.Bot(intents=intents)

# Load plugins
@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
    # Load all plugins first so commands are registered
    logger.info("Loading plugins...")
    for filename in os.listdir('./plugins'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                bot.load_extension(f'plugins.{filename[:-3]}')
                logger.info(f"Loaded plugin: {filename}")
            except Exception as e:
                logger.error(f"Failed to load plugin {filename}: {e}")
    
    # Now sync application commands with error handling
    logger.info("Syncing application commands...")
    
    try:
        # Sync to global scope for immediate availability
        logger.info("Syncing global commands...")
        await bot.sync_all_application_commands()
        
        # For faster testing, also sync to every guild the bot is in
        for guild in bot.guilds:
            logger.info(f"Syncing commands for guild: {guild.name} ({guild.id})")
            try:
                await bot.sync_application_commands(guild_id=guild.id)
            except Exception as guild_error:
                logger.error(f"Error syncing commands for guild {guild.name}: {guild_error}")
                
        logger.info("All slash commands synced successfully and should be available immediately")
    except nextcord.errors.NotFound as e:
        logger.warning(f"Error syncing commands: {e}")
        logger.info("Attempting alternative sync method...")
        try:
            # Alternative sync method
            await bot.sync_application_commands(force=True)
            logger.info("Commands synced using alternative method")
        except Exception as alt_error:
            logger.error(f"Alternative sync method failed: {alt_error}")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

# Start the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("No Discord token found. Please add DISCORD_TOKEN to your .env file.")
        exit(1)
    
    logger.info("Starting bot...")
    bot.run(DISCORD_TOKEN)
