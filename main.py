import os
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
import random
import datetime

jokes_list = [
    "Why don't scientists trust atoms? Because they make up everything.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "What do you call fake spaghetti? An impasta.",
    "How does a penguin build its house? Igloos it together.",
    "Why did the bicycle fall over? Because it was two-tired.",
    "How do you organize a space party? You planet.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What did the janitor say when he jumped out of the closet? Supplies!",
    "What's orange and sounds like a parrot? A carrot.",
    "How do you catch a squirrel? Climb a tree and act like a nut!",
    "Why couldn't the bicycle stand up by itself? It was two-tired.",
    "Why did the tomato turn red? Because it saw the salad dressing.",
    "What do you call a fish wearing a bowtie? Sofishticated.",
    "Why did the math book look sad? Because it had too many problems.",
    "What's a vampire's favorite fruit? A blood orange.",
    "How do you make a tissue dance? You put a little boogie in it.",
    "What did the ocean say to the shore? Nothing, it just waved.",
    "What did one wall say to the other wall? 'I'll meet you at the corner.'",
    "What did the grape do when it got stepped on? Nothing but let out a little wine.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "Why did the cookie go to the doctor? Because it was feeling crumbly.",
    "What do you call a factory that makes good products? A satisfactory.",
    "How does a penguin build its house? Igloos it together.",
    "What did one hat say to the other? 'Stay here, I'm going on ahead.'",
    "Why did the bicycle fall over? Because it was two-tired.",
    "What's the best time to go to the dentist? Tooth-hurty.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "Why did the chicken go to the seance? To talk to the other side.",
    "What do you call a fish wearing a crown? A kingfish.",
    "How do you organize a space party? You planet.",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What did the janitor say when he jumped out of the closet? Supplies!",
    "What's orange and sounds like a parrot? A carrot.",
    "How do you catch a squirrel? Climb a tree and act like a nut!",
    "Why couldn't the bicycle stand up by itself? It was two-tired.",
    "Why did the tomato turn red? Because it saw the salad dressing.",
    "What do you call a fish wearing a bowtie? Sofishticated.",
    "Why did the math book look sad? Because it had too many problems.",
    "What do you call a snowman with a six-pack? An abdominal snowman.",
    "Why did the bicycle fall over? Because it was two-tired.",
    "What's the best time to go to the dentist? Tooth-hurty.",
    "What did the scarecrow win an award? Because he was outstanding in his field.",
    "Why did the chicken go to the seance? To talk to the other side.",
    "What do you call a fish wearing a crown? A kingfish.",
    "How do you organize a space party? You planet.",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What did the janitor say when he jumped out of the closet? Supplies!",
    "What's orange and sounds like a parrot? A carrot.",
    "How do you catch a squirrel? Climb a tree and act like a nut!",
    "Why couldn't the bicycle stand up by itself? It was two-tired.",
    "Why did the tomato turn red? Because it saw the salad dressing.",
    "What do you call a fish wearing a bowtie? Sofishticated.",
    "Why did the math book look sad? Because it had too many problems.",
    "What do you call a snowman with a six-pack? An abdominal snowman.",
]

server_settings = {}

my_secret = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.messages = True
intents.message_reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_joke_from_website(url, selector):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        joke_div = soup.find(**selector)

        if joke_div:
            joke = joke_div.get_text().strip()
            return joke
        else:
            return None
    else:
        return None

def get_joke_from_sources():
    sources = [
        {
            'url': 'https://www.ajokeaday.com/',
            'selector': {'div': {'class': 'jd-body jubilat'}}
        },
        {
            'url': 'https://laffgaff.com/funny-joke-of-the-day/',
            'selector': {'div': {'class': 'entry-summary', 'itemprop': 'text'}}
        },
        {
            'url': 'https://jokesoftheday.net/',
            'selector': {'div': {'class': 'jokeContent'}}
        }
    ]

    for source in sources:
        joke = get_joke_from_website(source['url'], source['selector'])
        if joke:
            return joke
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    daily_joke.start()

@tasks.loop(hours=24)
async def daily_joke():
    now = datetime.datetime.now()
    if now.hour == 12 and now.minute == 0:  # Run only at noon
        joke = get_joke_from_sources()

        if joke:
            for server_id, settings in server_settings.items():
                channel_id = settings.get("channel_id")
                if channel_id:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        message = await channel.send(f"Here's your daily joke: {joke}")
                        print(f"Daily joke fetched for server {server_id}.")
                    else:
                        print(f"Channel not found for server {server_id}. Make sure the bot has the necessary permissions.")
        else:
            print("Failed to fetch daily joke from all sources.")

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '👎' and not user.bot:  # Check for thumbs down reaction
        message = reaction.message
        count = sum(1 for reaction in message.reactions if reaction.emoji == '👎')
        if count >= 3:  # Threshold for downvotes
            joke = get_joke_from_sources()  # Fetch the next joke
            if joke:
                await message.channel.send(f"The daily joke was unpopular. Here's another one: {joke}")
                await message.delete()  # Delete the unpopular joke
            else:
                await message.channel.send("No more jokes available for today.")
                await message.clear_reaction('👎')  # Clear reactions if no more jokes available

@bot.command(name='setup')
async def setup_command(ctx):
    server_id = str(ctx.guild.id)
    if server_id not in server_settings:
        server_settings[server_id] = {}

    await ctx.send("Please mention the channel where you want to receive daily jokes.")
    try:
        message = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author)
        channel_id = int(message.content.replace("<#", "").replace(">", ""))
        server_settings[server_id]["channel_id"] = channel_id
        await ctx.send(f"Daily jokes will be sent to <#{channel_id}>.")
    except ValueError:
        await ctx.send("Invalid channel ID. Please run the setup command again.")
    except asyncio.TimeoutError:
        await ctx.send("Setup timed out. Run the setup command again if you wish to configure the bot.")

@bot.command(name='joke')
async def joke_command(ctx):
    joke = get_joke_from_sources()
    if joke:
        await ctx.send(f"Sure, here's the daily joke: {joke}")
    else:
        await ctx.send("Sorry, I couldn't fetch a joke right now.")

@bot.command(name='jokes')
async def jokes_command(ctx):
    await ctx.send(random.choice(jokes_list))

bot.run(my_secret)
