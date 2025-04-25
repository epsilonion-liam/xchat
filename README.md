# Cross-Platform Chat Bot

A product of [Tempest Solutions](https://tempest-solutions.org.uk/)

## Legal Notice
This software is developed and maintained by Tempest Solutions, a company regulated by UK and international laws and regulations. Cross-Platform Chat Bot, along with Server Companion and Clan Commander, are official products of Tempest Solutions.

## Overview
This bot enables seamless communication between Discord and Telegram platforms. Users can chat across platforms while maintaining their native chat experience. Messages sent in a designated Discord channel are automatically forwarded to a linked Telegram chat, and vice versa.

### Key Features
- Two-way message relay between Discord and Telegram
- Admin-only configuration via Discord slash commands
- Persistent configuration storage
- Platform-specific message formatting
- Easy setup and configuration

## Dependencies
- Python 3.8 or higher
- nextcord (discord.py is discontinued)
- python-telegram-bot (v20 or higher)
- python-dotenv
- httpx

## Installation

1. Clone this repository
```bash
git clone https://github.com/Tempest-Solutions-Company/xchat
cd cross-platform-bot
```

2. Install required packages

### Basic Installation (Discord only)
If you only need Discord functionality, you can install with:
```bash
pip install nextcord python-dotenv
```

### Complete Installation (Discord + Telegram)
For full cross-platform functionality including Telegram:
```bash
pip install nextcord python-telegram-bot>=20.0 python-dotenv httpx
```

3. Create and configure the `.env` file
```plaintext
DISCORD_TOKEN=your_discord_bot_token_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
```

## Bot Setup

### Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the Bot section and create a bot
4. Enable the following Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Copy the bot token to your `.env` file
6. Generate an invite link with the following permissions:
   - Send Messages
   - Read Messages/View Channels
   - Manage Messages
   - Embed Links
7. Add the bot to your server using the generated invite link

### Telegram Bot Setup
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot using the `/newbot` command
3. Copy the bot token to your `.env` file
4. (Optional but recommended) Disable privacy mode:
   - Send `/mybots` to BotFather
   - Select your bot
   - Choose "Bot Settings"
   - Select "Group Privacy"
   - Select "Turn off"

## Linking Discord and Telegram

### Important Note About Permissions
All configuration slash commands in this bot require Discord Administrator permissions. This is by design to prevent unauthorized users from changing your bot's configuration. Only server administrators can run the setup and configuration commands.

### Step 1: Set Up Discord Channel
1. Run the bot using `python main.py`
2. In Discord, go to the channel you want to use for cross-platform chat
3. Use the command `/set_chat_channel #your-channel-name` (requires administrator permissions)
4. The bot will confirm the channel has been set up

### Step 2: Add Bot to Telegram Group
1. In Discord, use the command `/telegram_invite_link` (requires administrator permissions)
2. Add the bot to your Telegram group using the provided link
3. Make the bot an admin in the Telegram group (this is important!)
4. Send a message in the Telegram group

### Step 3: Get Telegram Chat ID
1. In your Telegram group, send the command `/chatid` or `/id`
2. The bot will reply with the chat ID (usually looks like `-123456789`)
3. Copy this chat ID
4. Alternatively, use `/get_telegram_updates` in Discord to see recent messages and chat IDs

### Step 4: Link Discord and Telegram
1. In Discord, use the command `/link_telegram -123456789` (replace with your actual chat ID)
2. The bot will confirm the successful linking
3. Test the connection by sending a message in Discord and checking if it appears in Telegram
4. Send a message in Telegram and check if it appears in Discord

## Available Commands

### Essential Commands
- `/status` - Show the current status of your cross-platform integration
- `/set_chat_channel` - Set the Discord channel for cross-platform chat
- `/link_telegram` - Link a Telegram chat to the current Discord channel
- `/telegram_invite_link` - Get an invite link for your Telegram bot

### Utility Commands
- `/reset_telegram_config` - Reset all Telegram chat configurations
- `/explain_crosschat` - Learn how the cross-platform chat works

## Troubleshooting

### Common Issues
1. **Messages not being relayed**:
   - Make sure the bot is an admin in your Telegram group
   - Verify that you're using the correct channel in Discord
   - Check that the chat ID format is correct (group IDs usually start with a minus sign)

2. **Privacy Mode Issues**:
   - By default, Telegram bots have privacy mode enabled
   - Either make the bot an admin in the group OR
   - Disable privacy mode via BotFather

3. **Command errors**:
   - Verify you have admin permissions in Discord
   - Check that the bot has necessary permissions

4. **Getting the right Chat ID**:
   - Group chat IDs typically start with a minus sign (e.g., `-1001234567890`)
   - Make sure to include the minus sign when linking the chat

## License
This software is copyright © Tempest Solutions 2024-2025.

All rights reserved. This software is provided for use under the following conditions:
- You may use and modify this software for personal or organizational purposes
- You may not redistribute this software without explicit permission
- You must maintain all branding and attribution in user-facing elements
- You may not use this code for commercial purposes without permission from Tempest Solutions

The "Powered by Tempest Solutions" branding in message footers must be maintained in all deployments and modifications of this software.

## Branding and Legal Requirements
All messages relayed through this bot include a footer with "Powered by Tempest Solutions" which links to https://tempest-solutions.org.uk. This branding must be maintained as per the license agreement and company requirements.

## Contact Information
For licensing inquiries or commercial use permission:
- Website: https://tempest-solutions.org.uk
- Contact: info@tempest-solutions.org.uk
