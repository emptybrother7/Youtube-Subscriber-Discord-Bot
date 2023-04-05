import os
import discord
from discord.ext import tasks
from discord import Intents
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# Bot token and YouTube API key
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
CHANNEL_ID = os.environ['CHANNEL_ID']

# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

async def get_subscriber_count():
    try:
        request = youtube.channels().list(
            part='statistics',
            id=CHANNEL_ID
        )
        response = request.execute()
        return int(response['items'][0]['statistics']['subscriberCount'])
    except HttpError as e:
        print(f'An error occurred: {e}')
        return None

class MyBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.update_status.start()

    @tasks.loop(minutes=60)
    async def update_status(self):
        subscriber_count = await get_subscriber_count()
        if subscriber_count is not None:
            activity = discord.Activity(type=discord.ActivityType.watching, name=f"{subscriber_count} subscribers")
            await self.change_presence(status=discord.Status.online, activity=activity)
        else:
            print('Failed to update the bot status due to an error in getting subscriber count.')

client = MyBot(intents=Intents.default())
client.run(DISCORD_BOT_TOKEN)

