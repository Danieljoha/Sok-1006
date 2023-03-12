import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup



# Load environment variables from .env file
load_dotenv(dotenv_path=r'C:\Users\Daniel\Documents\Rstudio GIT\Sok-1006\Sok-1006\Mappeoppgave\Discord\secret_bot.env')

# Read the Discord bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv('secret_bot')



# Create a new Discord bot instance
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='', intents=intents)

# Define a function to scrape the website and check for rows with specific keywords
def check_course_plan():
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
    for row in rows:
        if any("task" in value.lower() or "assignment" in value.lower() or "deadline" in value.lower() for value in row.values()):
            return f"Session: {row['Session']}\nTopics/Resources: {row['Topics/Resources']}"

# Define a command to check the course plan and post the result to Discord
@bot.command(name='check')
async def check_command(ctx):
    print('Received check command from', ctx.author.name)
    result = check_course_plan()
    if result:
        await ctx.send(f"A row was added that contains 'task', 'assignment', or 'deadline'.\n{result}")
    else:
        await ctx.send("No rows were added that contain 'task', 'assignment', or 'deadline'.")



# Run the Discord bot using the token from the environment variable
bot.run(DISCORD_BOT_TOKEN)
