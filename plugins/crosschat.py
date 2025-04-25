# ▀▀█▀▀ ▒█▀▀▀ ▒█▀▄▀█ ▒█▀▀█ ▒█▀▀▀ ▒█▀▀▀█ ▀▀█▀▀ 
#  ▒█   ▒█▀▀▀ ▒█▒█▒█ ▒█▄▄█ ▒█▀▀▀ ░▀▀▀▄▄  ▒█   
#  ▒█   ▒█▄▄▄ ▒█░░▒█ ▒█    ▒█▄▄▄ ▒█▄▄▄█  ▒█   

# ▒█▀▀▀█ ▒█▀▀▀█ ▒█░░░ ▒█░▒█ ▀▀█▀▀ ▀█▀ ▒█▀▀▀█ ▒█▄░▒█ ▒█▀▀▀█ 
# ░▀▀▀▄▄ ▒█░░▒█ ▒█░░░ ▒█░▒█ ░▒█░░ ▒█░ ▒█░░▒█ ▒█▒█▒█ ░▀▀▀▄▄ 
# ▒█▄▄▄█ ▒█▄▄▄█ ▒█▄▄█ ░▀▄▄▀ ░▒█░░ ▄█▄ ▒█▄▄▄█ ▒█░░▀█ ▒█▄▄▄█

#                           1997 - 2025
                           
#               Regulated by UK and International laws
#                 https://tempest-solutions.org.uk/

import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import json
import os
import logging
from dotenv import load_dotenv
import threading
import asyncio
import concurrent.futures
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramManager:
    """Class to handle all Telegram-specific functionality"""
    
    def __init__(self, config_manager, relay_callback):
        self.config_manager = config_manager
        self.relay_callback = relay_callback
        self.bot = None
        self.app = None
        self.initialize()
        
    def initialize(self):
        """Initialize Telegram bot if possible"""
        try:
            # Force reload dotenv to ensure we have the latest values
            load_dotenv(override=True)
            self.telegram_token = os.getenv('TELEGRAM_TOKEN')
            
            if not self.telegram_token:
                logger.warning("No TELEGRAM_TOKEN found in environment. Telegram integration disabled.")
                return False
            
            logger.info(f"Telegram token found, length: {len(self.telegram_token)}")
            
            # Try to import the necessary modules
            try:
                import telegram
                logger.info(f"Found telegram module version: {telegram.__version__}")
                
                # Handle different API versions
                if int(telegram.__version__.split('.')[0]) >= 20:
                    # Using v20+ API
                    from telegram import Bot, Update
                    from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
                    
                    # Initialize application
                    logger.info("Initializing with Telegram API v20+")
                    self.app = Application.builder().token(self.telegram_token).build()
                    self.bot = self.app.bot
                    
                    # Add message handler for v20+
                    async def telegram_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                        if update.message and update.message.text:
                            chat_id = str(update.message.chat_id)
                            text = update.message.text
                            sender = update.message.from_user.first_name
                            
                            # Call the relay callback
                            await self.relay_callback(chat_id, text, sender)
                    
                    # Add command handler for /chatid
                    async def chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                        """Send chat ID when /chatid command is received"""
                        chat = update.effective_chat
                        user = update.effective_user
                        
                        # Fix the markdown formatting to avoid parsing errors
                        try:
                            # Create a simple message with proper markdown escaping
                            message_text = (
                                "📢 *Chat Information*\n\n"
                                f"*Chat ID:* `{chat.id}`\n"
                                f"*Chat Type:* {chat.type}\n"
                            )
                            
                            # Add title for groups/channels
                            if hasattr(chat, 'title') and chat.title:
                                # Escape any potential markdown characters in the title
                                safe_title = chat.title.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
                                message_text += f"*Chat Title:* {safe_title}\n"
                            
                            # Add user information
                            message_text += f"\n*Your User ID:* `{user.id}`\n"
                            
                            if hasattr(user, 'username') and user.username:
                                message_text += f"*Your Username:* @{user.username}\n"
                            elif hasattr(user, 'first_name') and user.first_name:
                                # Escape any potential markdown characters in the name
                                safe_name = user.first_name.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
                                message_text += f"*Your Name:* {safe_name}\n"
                            
                            # Add instructions with proper escaping - make it explicit that command should be run in Discord
                            message_text += (
                                f"\n*To link this chat to Discord:*\n"
                                f"1. Copy this chat ID: `{chat.id}`\n"
                                f"2. Go to Discord and run this command in your server:\n"
                                f"   `/link_telegram {chat.id}`\n"
                                f"3. Make sure this bot is an admin in this Telegram chat"
                            )
                            
                            # Send message
                            await update.message.reply_text(
                                message_text,
                                parse_mode="Markdown"
                            )
                            
                            # Log the command
                            logger.info(f"Sent chat ID info to chat {chat.id} (type: {chat.type})")
                        except Exception as e:
                            # If markdown parsing fails, try without formatting
                            logger.error(f"Error sending formatted chat ID: {e}")
                            
                            # Fallback to plain text without markdown
                            plain_text = (
                                f"Chat Information\n\n"
                                f"Chat ID: {chat.id}\n"
                                f"Chat Type: {chat.type}\n"
                                f"To link this chat to Discord, use the command:\n"
                                f"/link_telegram {chat.id}"
                            )
                            
                            await update.message.reply_text(plain_text)
    
                    # Register the handlers
                    self.app.add_handler(
                        MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler)
                    )
                    self.app.add_handler(CommandHandler("chatid", chat_id_command))
                    self.app.add_handler(CommandHandler("id", chat_id_command))  # Alias
                    
                    # Start polling in a completely separate thread that manages its own event loop
                    self._start_polling_thread()
                    
                    logger.info("Telegram polling started successfully with v20+ API")
                    return True
                    
                else:
                    # We don't need to support older versions
                    logger.error("Telegram API version too old, requires v20+")
                    return False
                
            except Exception as e:
                logger.error(f"Error in Telegram setup: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                self.bot = None
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Telegram: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.bot = None
            return False

    def _start_polling_thread(self):
        """Start polling in a separate thread with its own event loop"""
        def run_telegram_polling():
            """Run Telegram polling in a separate thread with its own event loop"""
            try:
                # Create and run a new event loop for Telegram
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                
                # Run the application - this is the correct way for v20+
                # First initialize
                new_loop.run_until_complete(self.app.initialize())
                
                # Then run polling - note the method name change in v20+
                from telegram import Update
                new_loop.run_until_complete(
                    self.app.run_polling(allowed_updates=Update.ALL_TYPES)
                )
                
                # Should not reach here as run_polling blocks
                new_loop.run_forever()
            except Exception as e:
                logger.error(f"Error in Telegram polling thread: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Create and start the thread
        polling_thread = threading.Thread(target=run_telegram_polling, daemon=True)
        polling_thread.start()

    async def send_message(self, chat_id, message):
        """Send a message to Telegram with robust error handling"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
            
        try:
            # Escape special characters in the message content to avoid Markdown parsing issues
            author_name = message.author.name.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
            safe_content = message.content.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
            
            # Create properly formatted text
            text = f"*[Discord] {author_name}*\n{safe_content}"
            
            # Add attachments if any
            if message.attachments:
                attachment_list = []
                for attachment in message.attachments:
                    attachment_list.append(attachment.url)
                
                if attachment_list:
                    text += "\n\n*Attachments:*"
                    for url in attachment_list:
                        text += f"\n{url}"
            
            # Create one-time use bot instance to avoid event loop issues
            formatted_chat_id = int(chat_id)  # First try as-is
            
            # Try sending approaches in order of preference
            success = await self._try_send_plain_text(formatted_chat_id, message)
            if success:
                return True
                
            success = await self._try_send_markdown(formatted_chat_id, text)
            if success:
                return True
                
            # If chat ID might be in wrong format, try with negative
            if not str(chat_id).startswith('-'):
                negative_id = int(f"-{chat_id}")
                
                success = await self._try_send_plain_text(negative_id, message)
                if success:
                    # Update the config with the correct ID format
                    logger.info(f"Updating chat ID in config from {chat_id} to {negative_id}")
                    chat_data = self.config_manager.config['telegram_chats'].pop(str(chat_id), None)
                    if chat_data:
                        self.config_manager.config['telegram_chats'][str(negative_id)] = chat_data
                        self.config_manager.save()
                    return True
                    
                success = await self._try_send_markdown(negative_id, text)
                if success:
                    # Update the config with the correct ID format
                    logger.info(f"Updating chat ID in config from {chat_id} to {negative_id}")
                    chat_data = self.config_manager.config['telegram_chats'].pop(str(chat_id), None)
                    if chat_data:
                        self.config_manager.config['telegram_chats'][str(negative_id)] = chat_data
                        self.config_manager.save()
                    return True
            
            # If we get here, all attempts failed
            logger.error(f"All attempts to send message to Telegram chat {chat_id} failed")
            return False
            
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def _try_send_plain_text(self, chat_id, message):
        """Try sending a plain text message (most reliable)"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"[Discord] {message.author.name}\n{message.content}"
            }
            
            response = httpx.post(url, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent plain text message to Telegram chat {chat_id}")
                return True
            else:
                logger.warning(f"Plain text message failed: {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Error sending plain text message: {str(e)}")
            return False

    async def _try_send_markdown(self, chat_id, text):
        """Try sending with Markdown formatting"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = httpx.post(url, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                logger.info(f"Successfully sent Markdown message to Telegram chat {chat_id}")
                return True
            else:
                logger.warning(f"Markdown message failed: {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Error sending Markdown message: {str(e)}")
            return False

    async def get_bot_info(self):
        """Get information about the bot"""
        if not self.bot:
            return None
            
        try:
            # Use threading approach to avoid event loop conflicts
            def get_bot_info_thread():
                try:
                    # Create a new event loop for this thread
                    thread_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(thread_loop)
                    
                    # Define and run the async function
                    async def get_info_async():
                        try:
                            return await self.bot.get_me()
                        except Exception as e:
                            logger.error(f"Error getting bot info: {e}")
                            return None
                            
                    result = thread_loop.run_until_complete(get_info_async())
                    thread_loop.close()
                    return result
                except Exception as e:
                    logger.error(f"Thread error in get_bot_info: {e}")
                    return None
            
            # Execute the function in a new thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return executor.submit(get_bot_info_thread).result()
                
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    async def test_chat_access(self, chat_id):
        """Test if the bot can access a specific chat"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getChat"
            payload = {"chat_id": int(chat_id)}
            
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 200 and response.json().get('ok'):
                return response.json().get('result', {})
            else:
                return None
        except Exception as e:
            logger.error(f"Error testing chat access: {str(e)}")
            return None

    async def get_updates(self):
        """Get recent updates from Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
            response = httpx.get(url, params={"offset": -1, "limit": 10}, timeout=10.0)
            
            if response.status_code == 200 and response.json().get('ok'):
                return response.json().get('result', [])
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting Telegram updates: {str(e)}")
            return []


class ConfigManager:
    """Class to handle configuration management"""
    
    def __init__(self, config_file='crosschat_config.json'):
        self.config_file = config_file
        # Initialize with default values first
        self.config = {'discord_channels': {}, 'telegram_chats': {}}
        # Load configuration
        self.load()
        
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    logger.info(f"Loaded configuration from {self.config_file}")
                    
                    # Ensure all expected keys exist (backward compatibility)
                    if 'discord_channels' not in self.config:
                        self.config['discord_channels'] = {}
                    if 'telegram_chats' not in self.config:
                        self.config['telegram_chats'] = {}
            else:
                logger.info(f"No configuration file found, using defaults")
                self.save()  # Create the file with defaults
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Recover by using defaults
            self.config = {'discord_channels': {}, 'telegram_chats': {}}
            self.save()
            
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            
    def set_discord_channel(self, guild_id, channel_id):
        """Set the Discord channel for a guild"""
        self.config['discord_channels'][str(guild_id)] = channel_id
        self.save()
        
    def get_discord_channel(self, guild_id):
        """Get the Discord channel for a guild"""
        return self.config['discord_channels'].get(str(guild_id))
        
    def link_telegram_chat(self, chat_id, guild_id, channel_id):
        """Link a Telegram chat to a Discord channel"""
        if 'telegram_chats' not in self.config:
            self.config['telegram_chats'] = {}
            
        self.config['telegram_chats'][str(chat_id)] = {
            'guild_id': str(guild_id),
            'channel_id': channel_id
        }
        self.save()
        
    def get_linked_channel(self, chat_id):
        """Get the Discord channel linked to a Telegram chat"""
        if str(chat_id) not in self.config.get('telegram_chats', {}):
            return None
            
        data = self.config['telegram_chats'][str(chat_id)]
        return data.get('channel_id')
        
    def get_telegram_chats_for_guild(self, guild_id):
        """Get all Telegram chats linked to a guild"""
        result = []
        for chat_id, data in self.config.get('telegram_chats', {}).items():
            if data.get('guild_id') == str(guild_id):
                result.append(chat_id)
        return result
        
    def reset_telegram_config(self):
        """Reset all Telegram chat configurations"""
        old_config = self.config.get('telegram_chats', {}).copy()
        self.config['telegram_chats'] = {}
        self.save()
        return len(old_config)


class CrossPlatformChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_manager = ConfigManager()
        # Initialize Telegram manager with a callback for relaying messages
        self.telegram_manager = TelegramManager(
            self.config_manager, 
            self._telegram_message_callback
        )
        logger.info("CrossPlatformChat cog initialized")

    async def _telegram_message_callback(self, chat_id, text, sender_name):
        """Callback for when a message is received from Telegram"""
        # Process in Discord's event loop
        asyncio.run_coroutine_threadsafe(
            self.relay_to_discord(chat_id, text, sender_name),
            self.bot.loop
        )
    
    async def relay_to_discord(self, chat_id, text, sender_name):
        """Relay message from Telegram to Discord"""
        if chat_id in self.config_manager.config.get('telegram_chats', {}):
            data = self.config_manager.config['telegram_chats'][chat_id]
            channel_id = data.get('channel_id')
            if channel_id:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    embed = nextcord.Embed(description=text)
                    embed.set_author(name=f"[Telegram] {sender_name}")
                    footer_text = "Powered by Tempest Solutions"
                    # Fix: Use icon_url instead of url
                    embed.set_footer(text=footer_text, icon_url="https://tempest-solutions.org.uk/favicon.ico")
                    await channel.send(embed=embed)
                    logger.info(f"Relayed message from Telegram user {sender_name} to Discord channel {channel.name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle Discord messages to relay to Telegram"""
        if message.author.bot:
            return  # Ignore bot messages
            
        guild_id = str(message.guild.id)
        if guild_id in self.config_manager.config.get('discord_channels', {}):
            # Check if this is a designated cross-platform channel
            if message.channel.id == self.config_manager.config['discord_channels'][guild_id]:
                # Find telegram chats linked to this guild
                telegram_chats = self.config_manager.get_telegram_chats_for_guild(guild_id)
                for chat_id in telegram_chats:
                    await self.relay_to_telegram(chat_id, message)
    
    async def relay_to_telegram(self, chat_id, message):
        """Relay message from Discord to Telegram"""
        await self.telegram_manager.send_message(chat_id, message)

    @nextcord.slash_command(name="status", default_member_permissions=nextcord.Permissions(administrator=True))
    async def status(self, interaction: Interaction):
        """Show the current status of cross-platform integration"""
        embed = nextcord.Embed(title="Cross-Platform Chat Status", color=0x00ff00)
        
        # Discord channels
        discord_channels = []
        for guild_id, channel_id in self.config_manager.config.get('discord_channels', {}).items():
            guild = self.bot.get_guild(int(guild_id))
            channel = guild.get_channel(channel_id) if guild else None
            if channel:
                discord_channels.append(f"{guild.name}: {channel.mention}")
        
        embed.add_field(
            name="Discord Channels", 
            value="\n".join(discord_channels) if discord_channels else "No channels configured",
            inline=False
        )
        
        # Telegram linkages
        telegram_links = []
        for chat_id, data in self.config_manager.config.get('telegram_chats', {}).items():
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            guild = self.bot.get_guild(int(guild_id)) if guild_id else None
            channel = guild.get_channel(int(channel_id)) if guild and channel_id else None
            if channel:
                telegram_links.append(f"Chat ID {chat_id} → {channel.mention}")
        
        embed.add_field(
            name="Telegram Links", 
            value="\n".join(telegram_links) if telegram_links else "No Telegram chats linked",
            inline=False
        )
        
        # Update Telegram status
        if self.telegram_manager.bot:
            telegram_status = "Active - Messages are being relayed"
        else:
            telegram_status = "Inactive - Install python-telegram-bot and set TELEGRAM_TOKEN"
            
        embed.add_field(
            name="Telegram Integration Status", 
            value=telegram_status,
            inline=False
        )
        
        footer_text = "Powered by Tempest Solutions"
        # Fix: Use text with markdown link
        embed.set_footer(text="Powered by Tempest Solutions")
        
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="reset_telegram_config", default_member_permissions=nextcord.Permissions(administrator=True))
    async def reset_telegram_config(self, interaction: Interaction):
        """Reset Telegram chat configuration"""
        await interaction.response.defer(ephemeral=True)
        
        old_config = self.config_manager.reset_telegram_config()
        
        # Provide explanation of what was done
        await interaction.followup.send(f"✅ Reset Telegram chat configuration. Removed {old_config} chat links.\n\nUse `/link_telegram` with a valid chat ID to reconfigure.")

    @nextcord.slash_command(name="link_telegram", default_member_permissions=nextcord.Permissions(administrator=True))
    async def link_telegram(
        self,
        interaction: Interaction,
        chat_id: str = SlashOption(description="Telegram chat ID to link")
    ):
        """Link a Telegram chat to this Discord channel"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild_id)
        channel_id = interaction.channel_id
        
        # Validate that the chat ID can be parsed as an integer
        try:
            int(chat_id)
        except ValueError:
            await interaction.followup.send(
                "❌ Invalid chat ID format. The chat ID should be a number, like `-123456789`.",
                ephemeral=True
            )
            return
            
        # Add debugging
        logger.info(f"Linking Telegram chat ID {chat_id} to Discord channel {channel_id} in guild {guild_id}")
        logger.info(f"Config before update: {json.dumps(self.config_manager.config, indent=2)}")
        
        # Store the telegram chat to discord channel mapping
        self.config_manager.link_telegram_chat(chat_id, guild_id, channel_id)
        
        # Add debugging
        logger.info(f"Config after update: {json.dumps(self.config_manager.config, indent=2)}")
        
        # We need to modify this part since it references test_chat_access
        try:
            # Use direct API call to test chat access
            import httpx
            telegram_token = os.getenv('TELEGRAM_TOKEN')
            url = f"https://api.telegram.org/bot{telegram_token}/getChat"
            payload = {"chat_id": int(chat_id)}
            
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 200 and response.json().get('ok'):
                chat_data = response.json().get('result', {})
                chat_type = chat_data.get('type', 'unknown')
                chat_title = chat_data.get('title', chat_data.get('username', 'Unknown'))
                
                await interaction.followup.send(
                    f"✅ Successfully linked Telegram chat: **{chat_title}** (Type: {chat_type}) to this Discord channel.\n\n"
                    f"Messages sent in this channel will now be relayed to Telegram and vice versa.",
                    ephemeral=True
                )
            else:
                error_text = "Chat not found or not accessible"
                if response.status_code != 200 and response.json().get('description'):
                    error_text = response.json().get('description')
                
                await interaction.followup.send(
                    f"⚠️ Configuration saved, but there might be issues: {error_text}\n\n"
                    f"Please make sure:\n"
                    f"1. Your bot has been added to the Telegram chat\n"
                    f"2. Your bot has permission to send messages\n"
                    f"3. The chat ID ({chat_id}) is correct\n\n"
                    f"Use `/telegram_help` for more information on setting up the bot correctly.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error testing Telegram chat: {e}")
            await interaction.followup.send(
                f"⚠️ Configuration saved, but could not verify access to the chat: {str(e)}\n\n"
                f"Use `/telegram_help` for help with setting up your bot correctly.",
                ephemeral=True
            )

    @nextcord.slash_command(name="set_chat_channel", default_member_permissions=nextcord.Permissions(administrator=True))
    async def set_chat_channel(
        self,
        interaction: Interaction,
        channel: nextcord.TextChannel = SlashOption(description="Select channel for cross-platform chat")
    ):
        """Set the Discord channel for cross-platform chat"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild_id)
        previous_channel_id = self.config_manager.get_discord_channel(guild_id)
        
        # Update the Discord channel configuration
        self.config_manager.set_discord_channel(guild_id, channel.id)
        
        # Update all Telegram chats linked to this guild to use the new channel
        updated_chats = 0
        for chat_id, data in list(self.config_manager.config.get('telegram_chats', {}).items()):
            if data.get('guild_id') == guild_id:
                # Update to use the new channel ID
                self.config_manager.config['telegram_chats'][chat_id]['channel_id'] = channel.id
                updated_chats += 1
        
        # Save the config if any Telegram chats were updated
        if updated_chats > 0:
            self.config_manager.save()
            logger.info(f"Updated {updated_chats} Telegram chat links to use channel {channel.id} for guild {guild_id}")
        
        # Prepare response message
        response = f"✅ Cross-platform chat channel set to {channel.mention}\n\n"
        
        if updated_chats > 0:
            response += f"✅ Updated {updated_chats} Telegram chat links to use this channel.\n\n"
        
        response += "Messages in this channel will be relayed to linked Telegram chats and vice versa.\n"
        
        if updated_chats == 0:
            response += "Use `/link_telegram` to link a Telegram chat to this server."
        
        await interaction.followup.send(response, ephemeral=True)

    @nextcord.slash_command(name="telegram_invite_link", default_member_permissions=nextcord.Permissions(administrator=True))
    async def telegram_invite_link(self, interaction: Interaction):
        """Generate invitation links to add your bot to Telegram groups"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            import httpx
            telegram_token = os.getenv('TELEGRAM_TOKEN')
            
            # Get bot info using the token from your .env file
            url = f"https://api.telegram.org/bot{telegram_token}/getMe"
            response = httpx.get(url, timeout=5.0)
            
            if response.status_code != 200:
                await interaction.followup.send(
                    f"❌ Could not connect to Telegram API with your token. Please check your TELEGRAM_TOKEN in the .env file.",
                    ephemeral=True
                )
                return
                
            bot_info = response.json().get('result', {})
            bot_username = bot_info.get('username', 'Unknown')
            bot_id = bot_info.get('id', 'Unknown')
            
            # Create embed with links
            embed = nextcord.Embed(
                title="Telegram Bot Invitation Links",
                description=f"Use these links to add **@{bot_username}** (your configured bot) to groups and chats",
                color=0x00b0f4
            )
            
            # Add direct link
            embed.add_field(
                name="Add Bot to Group",
                value=f"[Click to add @{bot_username} to your group](https://t.me/{bot_username}?startgroup=true)",
                inline=False
            )
            
            # Add direct chat link
            embed.add_field(
                name="Start Direct Chat",
                value=f"[Start chatting with @{bot_username}](https://t.me/{bot_username})",
                inline=False
            )
            
            # Add manual instructions
            embed.add_field(
                name="Manual Addition Instructions",
                value=(
                    "**In Telegram:**\n"
                    "1. Open the group you want to add the bot to\n"
                    "2. Click the group name at the top\n"
                    "3. Select 'Add members'\n"
                    "4. Search for @" + bot_username + "\n"
                    "5. Select the bot and add it"
                ),
                inline=False
            )
            
            # Add privacy reminder
            embed.add_field(
                name="Important Reminder",
                value=(
                    "Your bot has privacy mode enabled (`can_read_all_group_messages: false`)\n\n"
                    "This means it **won't see regular messages** unless:\n"
                    "- Messages that start with / are sent\n"
                    "- Replies to the bot's messages are sent\n"
                    "- Messages in channels where they are admin are sent\n\n"
                    "Try making the bot an admin in your group to solve this."
                ),
                inline=False
            )
            
            # Add configuration clarification
            embed.add_field(
                name="⚠️ Bot Configuration",
                value=(
                    f"These links are for **@{bot_username}**, the bot configured in your `.env` file.\n\n"
                    f"If you create a new bot in Telegram, you must update your TELEGRAM_TOKEN in the .env file."
                ),
                inline=False
            )
            
            # Add next steps
            embed.add_field(
                name="After Adding to Group",
                value=(
                    "1. In Telegram, run the command `/chatid` in your group\n"
                    "2. Copy the chat ID shown (usually looks like `-123456789`)\n"
                    "3. Use `/link_telegram <chat_id>` in Discord with the ID you copied\n"
                    "4. Use `/set_chat_channel` to set which Discord channel will be linked"
                ),
                inline=False
            )
            
            footer_text = "Powered by Tempest Solutions"
            # Fix: Use proper parameter
            embed.set_footer(text=footer_text, icon_url="https://tempest-solutions.org.uk/favicon.ico")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error generating Telegram invite links: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await interaction.followup.send(f"Error generating Telegram invite links: {str(e)}")

    @nextcord.slash_command(name="explain_crosschat", default_member_permissions=nextcord.Permissions(administrator=True))
    async def explain_crosschat(self, interaction: Interaction):
        """Explains how the cross-platform chat bridge works"""
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="Cross-Platform Chat Bridge Explained",
            description="This bot creates a bridge between Discord and Telegram, allowing messages to flow in both directions.",
            color=0x00b0f4
        )
        
        # How it works section
        embed.add_field(
            name="How It Works",
            value=(

                "1. Messages sent in a designated Discord channel are forwarded to a linked Telegram chat\n"
                "2. Messages sent in the linked Telegram chat are forwarded to the designated Discord channel\n"
                "3. This creates a seamless chat experience across both platforms"
            ),
            inline=False
        )
        
        # Setup explanation - updated to remove outdated references
        embed.add_field(
            name="Setup Process",
            value=(
                "**Step 1:** Use `/set_chat_channel` to designate which Discord channel will be the bridge\n"
                "**Step 2:** Add your bot to the Telegram group/chat (use `/telegram_invite_link`)\n" 
                "**Step 3:** Make your bot an admin in the Telegram group\n"
                "**Step 4:** In Telegram, send `/chatid` to get the group's ID\n"
                "**Step 5:** Link the Telegram chat with `/link_telegram <chat_id>`"
            ),
            inline=False
        )
        
        # Message formatting explanation
        embed.add_field(
            name="Message Formatting",
            value=(

                "**Discord → Telegram:**\n"
                "Messages appear as: \"*[Discord] Username*\nMessage content\"\n\n"
                "**Telegram → Discord:**\n"
                "Messages appear in an embed with \"[Telegram] Username\" as the author"
            ),
            inline=False
        )
        
        # Privacy mode note
        embed.add_field(
            name="⚠️ Important Privacy Note",
            value=(

                "Your bot has privacy mode enabled, which means it can only see messages in Telegram when:\n"
                "• The bot is mentioned directly\n"
                "• Messages start with a command (/)\n"
                "• The bot is an admin in the group\n\n"
                "**Solution:** Make your bot an admin in the Telegram group"
            ),
            inline=False
        )
        
        # Available commands - updated to match actual commands
        embed.add_field(
            name="Available Commands",
            value=(
                "• `/status` - View current configuration\n"
                "• `/set_chat_channel` - Set up a Discord channel for cross-chat\n"
                "• `/link_telegram` - Connect a Telegram chat\n"
                "• `/telegram_invite_link` - Get links to add your bot to Telegram\n"
                "• `/reset_telegram_config` - Reset configuration if needed"
            ),
            inline=False
        )
        
        footer_text = "Powered by Tempest Solutions"
        embed.set_footer(text=footer_text, icon_url="https://tempest-solutions.org.uk/favicon.ico")
        
        await interaction.followup.send(embed=embed)

def setup(bot):
    """Setup function for the cog"""
    if bot is None:
        logger.error("Bot object is None in setup function")
        return
    
    try:
        logger.info("Adding CrossPlatformChat cog to bot")
        bot.add_cog(CrossPlatformChat(bot))
        logger.info("CrossPlatformChat cog added successfully")
    except Exception as e:
        logger.error(f"Error adding CrossPlatformChat cog: {e}")
