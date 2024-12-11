import discord
from discord.ext import commands

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

with open("token.txt") as file:
    token = file.read()

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Attempting to load extension: {filename}")
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Successfully loaded: {filename}")
            except Exception as e:
                print(f"Failed to load: {filename}\nError: {e}")

class TestMenuButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="A", style=discord.ButtonStyle.red)
    async def button_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="You've chosen Choice A.")
    
    @discord.ui.button(label="B", style=discord.ButtonStyle.blurple)
    async def button_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="You've chosen Choice B.")
    
    @discord.ui.button(label="C", style=discord.ButtonStyle.green)
    async def button_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="You've chosen Choice C.")
    
    @discord.ui.button(label="D", style=discord.ButtonStyle.gray)
    async def button_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="You've chosen Choice D.")

@bot.tree.command(name="buttonmenu", description="Prototype of Answer Buttons")
async def buttonmenu(interaction: discord.Interaction):
    await interaction.response.send_message(content="Please choose an answer:", view=TestMenuButton())

class SelectMenu(discord.ui.View):
    options = [
        discord.SelectOption(label="Flashcards", value="1", description="Study individually with flashcards."),
        discord.SelectOption(label="Solo Quiz", value="2", description="Study individually with multiple-choice questions."),
        discord.SelectOption(label="Team Quiz", value="3", description="Study in a group with multiple-choice questions.")
    ]

    @discord.ui.select(placeholder="Select Mode:", options=options)
    async def menu_callback(self, interaction: discord.Interaction, select):
        select.disabled=True
        if select.values[0] == "1":
            await interaction.response.send_message(content="You chose to play Flashcards")
        elif select.values[0] == "2":
            await interaction.response.send_message(content="You chose to play Solo Quiz")
        elif select.values[0] == "3":
            await interaction.response.send_message(content="Your color is now yellow")
        
@bot.tree.command(name="choosemode", description="Choose the mode you wish to play")
async def choosemode(interaction: discord.Interaction):
    await interaction.response.send_message(content="Choose the mode you wish to play", view=SelectMenu())




async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())