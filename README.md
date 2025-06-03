# Discord Tally Bot

A simple Discord bot that keeps track of user tallies with daily, weekly, and monthly statistics.

## Features
- Tracks user tallies with `!tally <number>` command
- Displays daily, weekly, and monthly counts
- Shows percentage of total tallies for each time period
- Data persists between bot restarts
- Automatic reset of counts at appropriate intervals

## Setup

1. **Install Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install required packages**
   ```
   pip install -r requirements.txt
   ```

3. **Create a Discord Bot**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" tab and click "Add Bot"
   - Copy the bot token

4. **Create a .env file**
   Create a file named `.env` in the project directory with:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```
   Replace `your_bot_token_here` with your bot's token.

5. **Invite the bot to your server**
   - Go to the "OAuth2" tab in the Developer Portal
   - Select "bot" under Scopes
   - Select necessary permissions (Send Messages, Read Message History, etc.)
   - Use the generated URL to add the bot to your server

## Usage
- Use `!tally <number>` to add to your tally
- Example: `!tally 5` will add 5 to your daily, weekly, and monthly tallies

The bot will respond with an embed showing your current tallies and percentages.

## Data Storage
Tally data is stored in `tally_data.json` in the bot's directory. This file is automatically created and updated by the bot.

## License
MIT
