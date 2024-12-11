import discord
from discord.ext import commands
from discord import app_commands

import os
import asyncio

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("bot is online")
    await bot.change_presence(activity=discord.Game(name='.help'))
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} command(s).")
    except Exception as e:
        print("An error with syncing application commands has occured: ", e)

#First Slash Command(will try to put them in a cog later)
@bot.tree.command(name="hello", description="Says hello to the person who ran the command")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Hello there!")

with open("token.txt") as file:
    token = file.read()

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())