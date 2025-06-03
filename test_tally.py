import json
from datetime import datetime, timedelta
from collections import defaultdict

class MockMessage:
    def __init__(self, author_id, author_name, content):
        self.author = MockUser(author_id, author_name)
        self.content = content
        self.created_at = datetime.utcnow()
    
    async def send(self, *args, **kwargs):
        # For testing purposes, we'll print the embed data
        if 'embed' in kwargs:
            embed = kwargs['embed']
            print("\n=== Bot Response ===")
            print(f"Author: {embed.author.name}")
            for field in embed.fields:
                print(f"{field.name}: {field.value}")
            print(f"Footer: {embed.footer.text}")
            print("===================\n")
        return self

class MockUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.display_name = name
        self.avatar = None

class MockContext:
    def __init__(self, message):
        self.message = message
        self.author = message.author
        self.send = message.send

class TallyBot:
    def __init__(self):
        self.tally_data = {
            'daily': defaultdict(int),
            'weekly': defaultdict(int),
            'monthly': defaultdict(int),
            'last_reset': {
                'daily': None,
                'weekly': None,
                'monthly': None
            }
        }
    
    async def process_tally(self, ctx, number: int):
        user_id = ctx.author.id
        
        # Update counts
        self.tally_data['daily'][user_id] = self.tally_data['daily'].get(user_id, 0) + number
        self.tally_data['weekly'][user_id] = self.tally_data['weekly'].get(user_id, 0) + number
        self.tally_data['monthly'][user_id] = self.tally_data['monthly'].get(user_id, 0) + number
        
        # Calculate totals and percentages
        daily_total = sum(self.tally_data['daily'].values())
        weekly_total = sum(self.tally_data['weekly'].values())
        monthly_total = sum(self.tally_data['monthly'].values())
        
        daily_percent = (self.tally_data['daily'][user_id] / daily_total * 100) if daily_total > 0 else 0
        weekly_percent = (self.tally_data['weekly'][user_id] / weekly_total * 100) if weekly_total > 0 else 0
        monthly_percent = (self.tally_data['monthly'][user_id] / monthly_total * 100) if monthly_total > 0 else 0
        
        # Create a mock embed-like dictionary for testing
        return {
            'author': {'name': f"{ctx.author.display_name}'s Tally:", 'icon_url': None},
            'fields': [
                {'name': 'Daily', 'value': f"{self.tally_data['daily'][user_id]:,} ({daily_percent:.2f}% of total)", 'inline': False},
                {'name': 'Weekly', 'value': f"{self.tally_data['weekly'][user_id]:,} ({weekly_percent:.2f}% of total)", 'inline': False},
                {'name': 'Monthly', 'value': f"{self.tally_data['monthly'][user_id]:,} ({monthly_percent:.2f}% of total)", 'inline': False}
            ],
            'footer': {'text': datetime.now().strftime("%m/%d/%y, %I:%M %p")}
        }

# Test the bot
async def test_tally():
    print("=== Starting Tally Bot Test ===\n")
    
    # Create test users
    user1 = MockUser(12345, "TestUser1")
    user2 = MockUser(67890, "TestUser2")
    
    # Create bot instance
    bot = TallyBot()
    
    # Test 1: First tally for user1
    print("Test 1: First tally for user1 (5)")
    msg1 = MockMessage(user1.id, user1.name, "!tally 5")
    ctx1 = MockContext(msg1)
    await bot.process_tally(ctx1, 5)
    
    # Print current state
    print("\nCurrent state after Test 1:")
    print(f"User1 daily: {bot.tally_data['daily'][user1.id]}")
    print(f"User1 weekly: {bot.tally_data['weekly'][user1.id]}")
    print(f"User1 monthly: {bot.tally_data['monthly'][user1.id]}\n")
    
    # Test 2: Second tally for user1 (3)
    print("Test 2: Second tally for user1 (3)")
    msg2 = MockMessage(user1.id, user1.name, "!tally 3")
    ctx2 = MockContext(msg2)
    result = await bot.process_tally(ctx2, 3)
    
    # Print the result (would be an embed in the real bot)
    print("\nBot would respond with:")
    print(f"{result['author']['name']}")
    for field in result['fields']:
        print(f"{field['name']}: {field['value']}")
    print(f"Footer: {result['footer']['text']}\n")
    
    # Test 3: Tally for user2 (10)
    print("Test 3: First tally for user2 (10)")
    msg3 = MockMessage(user2.id, user2.name, "!tally 10")
    ctx3 = MockContext(msg3)
    result = await bot.process_tally(ctx3, 10)
    
    # Print the result
    print("\nBot would respond with:")
    print(f"{result['author']['name']}")
    for field in result['fields']:
        print(f"{field['name']}: {field['value']}")
    print(f"Footer: {result['footer']['text']}")
    
    print("\n=== Test Complete ===")

# Run the test
import asyncio
asyncio.run(test_tally())
