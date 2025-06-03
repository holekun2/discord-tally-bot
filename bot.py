import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from collections import defaultdict
import json

# Bot setup - Explicitly define only the intents we need
intents = discord.Intents(
    guilds=True,           # Basic guild info
    messages=True,         # Message events
    message_content=True,  # Required for command content
    # Everything else False
    members=False,
    presences=False,
    voice_states=False,
    typing=False,
    reactions=False,
    emojis=False,
    webhooks=False,
    integrations=False,
    invites=False,
    bans=False,
    emojis_and_stickers=False,
    guild_reactions=False,
    guild_typing=False,
    integrations_enabled=False,
    webhooks_enabled=False,
    invites_enabled=False,
    voice=False,
    guild_scheduled_events=False,
    auto_moderation=False,
    auto_moderation_configuration=False,
    auto_moderation_execution=False
)

# Initialize bot with minimal configuration
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None,  # Disable default help command
    case_insensitive=True
)

# Data storage
tally_data = {
    'daily': defaultdict(int),
    'weekly': defaultdict(int),
    'monthly': defaultdict(int),
    'last_reset': {
        'daily': None,
        'weekly': None,
        'monthly': None
    }
}

# File to store data
DATA_FILE = 'tally_data.json'

# Load data from file if it exists
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert user IDs back to integers (JSON keys are always strings)
            tally_data['daily'] = {int(k): v for k, v in data.get('daily', {}).items()}
            tally_data['weekly'] = {int(k): v for k, v in data.get('weekly', {}).items()}
            tally_data['monthly'] = {int(k): v for k, v in data.get('monthly', {}).items()}
            tally_data['last_reset'] = data.get('last_reset', {
                'daily': None,
                'weekly': None,
                'monthly': None
            })

# Save data to file
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(tally_data, f, indent=2)

# Check and reset tallies if needed
def check_reset():
    now = datetime.utcnow()
    
    # Check daily reset (every day at midnight UTC)
    if tally_data['last_reset']['daily'] is None or \
       (now - datetime.fromisoformat(tally_data['last_reset']['daily'])).days >= 1:
        if now.hour >= 0:  # Only reset if it's past midnight
            tally_data['daily'] = defaultdict(int)
            tally_data['last_reset']['daily'] = now.isoformat()
    
    # Check weekly reset (every Monday at midnight UTC)
    if tally_data['last_reset']['weekly'] is None or \
       (now - datetime.fromisoformat(tally_data['last_reset']['weekly'])).days >= 7:
        if now.weekday() == 0 and now.hour >= 0:  # Monday and past midnight
            tally_data['weekly'] = defaultdict(int)
            tally_data['last_reset']['weekly'] = now.isoformat()
    
    # Check monthly reset (first day of month at midnight UTC)
    if tally_data['last_reset']['monthly'] is None or \
       (now.month != datetime.fromisoformat(tally_data['last_reset']['monthly']).month):
        if now.day == 1 and now.hour >= 0:  # First day of month and past midnight
            tally_data['monthly'] = defaultdict(int)
            tally_data['last_reset']['monthly'] = now.isoformat()
    
    save_data()

# Background task to check for resets
@tasks.loop(minutes=30)
async def check_reset_task():
    check_reset()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    load_data()
    check_reset()
    check_reset_task.start()

@bot.command()
async def tally(ctx, number: int):
    """Add to your tally count"""
    if number <= 0:
        await ctx.send("Please provide a positive number.")
        return
    
    user_id = ctx.author.id
    
    # Update counts
    tally_data['daily'][user_id] = tally_data['daily'].get(user_id, 0) + number
    tally_data['weekly'][user_id] = tally_data['weekly'].get(user_id, 0) + number
    tally_data['monthly'][user_id] = tally_data['monthly'].get(user_id, 0) + number
    
    # Calculate percentages
    daily_total = sum(tally_data['daily'].values())
    weekly_total = sum(tally_data['weekly'].values())
    monthly_total = sum(tally_data['monthly'].values())
    
    daily_percent = (tally_data['daily'][user_id] / daily_total * 100) if daily_total > 0 else 0
    weekly_percent = (tally_data['weekly'][user_id] / weekly_total * 100) if weekly_total > 0 else 0
    monthly_percent = (tally_data['monthly'][user_id] / monthly_total * 100) if monthly_total > 0 else 0
    
    # Create embed
    embed = discord.Embed(color=discord.Color.blue())
    embed.set_author(name=f"{ctx.author.display_name}'s Tally:", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    embed.add_field(name="Daily", 
                   value=f"{tally_data['daily'][user_id]:,} ({daily_percent:.2f}% of total)", 
                   inline=False)
    embed.add_field(name="Weekly", 
                   value=f"{tally_data['weekly'][user_id]:,} ({weekly_percent:.2f}% of total)", 
                   inline=False)
    embed.add_field(name="Monthly", 
                   value=f"{tally_data['monthly'][user_id]:,} ({monthly_percent:.2f}% of total)", 
                   inline=False)
    
    # Set footer with current time in the specified format
    current_time = datetime.now().strftime("%-m/%-d/%y, %-I:%M %p")
    embed.set_footer(text=current_time)
    
    await ctx.send(embed=embed)
    save_data()

# Run the bot
if __name__ == "__main__":
    # Load token from environment variable
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set!")
        print("Please create a .env file with DISCORD_TOKEN=your_token_here")
    else:
        bot.run(TOKEN)
