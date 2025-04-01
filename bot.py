import discord
import asyncio
import requests
from bs4 import BeautifulSoup

TOKEN = 'DISCORD_TOKEN'
CHANNEL_ID = 1270664553902116948  # Replace with the channel ID you want to send the message to

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def fetch_wow_token_price():
    url = 'https://wowauction.us/token'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    current_tag = soup.find("b", string="Current:")
    if current_tag:
        for sibling in current_tag.next_siblings:
            if sibling.string and sibling.string.strip():
                price_text = sibling.string.strip()
                return price_text.replace(",", "")
    return None

async def periodic_task():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found!")
        return
    while not client.is_closed():
        try:
            price = fetch_wow_token_price()
            if price:
                await channel.send(f'The current US WoW token price is {price} gold.')
            else:
                await channel.send('Could not retrieve the WoW token price at this time.')
        except Exception as e:
            await channel.send(f'An error occurred: {e}')
        # Sleep for 10 minutes (600 seconds)
        await asyncio.sleep(600)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    # Start the background task
    client.loop.create_task(periodic_task())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == '!wowtoken':
        try:
            price = fetch_wow_token_price()
            if price:
                await message.channel.send(f'The current US WoW token price is {price} gold.')
            else:
                await message.channel.send('Could not retrieve the WoW token price at this time.')
        except Exception as e:
            await message.channel.send(f'An error occurred: {e}')

client.run(TOKEN)
