import os , sys
import discord
from discord.ext import commands

token = ''
client = commands.Bot(command_prefix='!', intents= discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user.name} is ready to rock!')
cogfiles = [
    f"cogs.{filename[:-3]}" for filename in os.listdir("cogs") if filename.endswith(".py")
]
for cog in cogfiles:
    try:
        client.load_extension(cog)
    except Exception as err:
        print(f"Failed to load extension {cog}.", file=sys.stderr)

client.run(token)