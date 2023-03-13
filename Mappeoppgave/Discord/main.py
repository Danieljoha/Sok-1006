import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import asyncio

# Load environment variables from .env file
load_dotenv(dotenv_path=r'Mappeoppgave\Discord\secret_bot.env')

# Read the Discord bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv('secret_bot')

# Create a new Discord bot instance
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Define a function to scrape the website and check for rows with specific keywords
last_match = None  # Initialize last_match to None to indicate that no matching rows have been found yet

async def post_new_row(row):
    # Define a function to post the new row to Discord
    channel = bot.get_channel(1065637170708222052)  # ID of the Discord channel where it posts
    await channel.send(f"God dag god dag studentan \nNy oppgave i Sok-1005:\n{row}")

async def check_course_plan():
    global last_match  # Access the global last_match variable

    url = 'https://uit-sok-1005-v23.github.io/courseplan.html'

    # make a GET request to the website and get the HTML content
    response = requests.get(url)
    html_content = response.text

    # parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # find the table on the page
    table = soup.find('table')

    # get the column headers
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # get the rows in the table
    rows = []
    for tr in table.find_all('tr')[1:]:
        row = {}
        for index, td in enumerate(tr.find_all('td')):
            row[headers[index]] = td.text.strip()
        rows.append(row)

    # check each row for the words "task", "assignment", and "deadline"
    latest_match = None
    for row in rows:
        if any("task" in value.lower() or "assignment" in value.lower() or "deadline" in value.lower() for value in row.values()):
            latest_match = f"{row['Date']} {row['Session']} {row['Topics/Resources']}"

    if latest_match and latest_match != last_match:
        # If a new matching row has been found, and it is different from the last known matching row,
        # then assume that a new row has been added and return it
        last_match = latest_match  # Update the last_match variable to the latest matching row
        await post_new_row(latest_match) # Post the new row to Discord
        return latest_match
    
    # If no new matching row has been found, return None
    return None

async def periodic_check():
    while True:
        await check_course_plan() # Wait for the result of check_course_plan()
        await asyncio.sleep(60 * 5)  # Wait for 5 minutes before checking again

# Start the periodic check loop asynchronously
async def start_periodic_check():
    asyncio.create_task(periodic_check())


# Define a command to check the course plan and post the result to Discord
@bot.command(name='check')
async def check_command(ctx):
    print('Received check command from', ctx.author.name)
    result = await check_course_plan()  # Await the result of check_course_plan()
    if result:
        await ctx.send(f"God dag god dag studentan \nNy oppgave i Sok-1005:\n{result}")
    else:
        # Check if the last_match variable has been set to a non-None value
        if last_match is not None:
            await ctx.send("Ikke noe nytt arbeid.")


# Run the Discord bot using the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
