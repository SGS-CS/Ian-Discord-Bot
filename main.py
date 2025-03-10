import discord
from discord.ext import commands

import os
import asyncio
import sqlite3


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
            await interaction.response.send_message(content="You chose to play Flashcards.")
        elif select.values[0] == "2":
            await interaction.response.send_message(content="You chose to play Solo Quiz.")
        elif select.values[0] == "3":
            await interaction.response.send_message(content="You chose to play Team Quiz.")
        
@bot.tree.command(name="choosemode", description="Choose the mode you wish to play")
async def choosemode(interaction: discord.Interaction):
    await interaction.response.send_message(content="Choose the mode you wish to play", view=SelectMenu())

@bot.tree.command(name="createquestion", description="Add a question to a quiz")
@discord.app_commands.describe(
    question="The quiz question",
    choice_a="Option A",
    choice_b="Option B",
    choice_c="Option C",
    choice_d="Option D",
    correct_answer="The correct answer (A, B, C, or D)"
)
@discord.app_commands.choices(correct_answer=[
    discord.app_commands.Choice(name="A", value="A"),
    discord.app_commands.Choice(name="B", value="B"),
    discord.app_commands.Choice(name="C", value="C"),
    discord.app_commands.Choice(name="D", value="D"),
])
async def createquestion(interaction: discord.Interaction, question: str, choice_a: str, choice_b: str, choice_c: str, choice_d: str, correct_answer: str):
    
    # Store the data in the database
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO questions (question, choice_a, choice_b, choice_c, choice_d, correct_choice)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (question, choice_a, choice_b, choice_c, choice_d, correct_answer))
    conn.commit()
    conn.close()

    await interaction.response.send_message(
        f"**Question added!**\n"
        f"**Q:** {question}\n"
        f"**A:** {choice_a}\n"
        f"**B:** {choice_b}\n"
        f"**C:** {choice_c}\n"
        f"**D:** {choice_d}\n"
        f"**Correct Answer:** {correct_answer}",
        ephemeral=True
    )

@bot.tree.command(name="runquiz", description="Start a quiz session")
async def runquiz(interaction: discord.Interaction):
    # Defer response to prevent timeout
    await interaction.response.defer(thinking=True)

    # Connect to database and get a random question
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, choice_a, choice_b, choice_c, choice_d, correct_choice FROM questions ORDER BY RANDOM() LIMIT 1")
    question_data = cursor.fetchone()
    conn.close()

    if not question_data:
        await interaction.followup.send("No questions found in the database!", ephemeral=True)
        return

    question_id, question, choice_a, choice_b, choice_c, choice_d, correct_answer = question_data

    # Create an embed for the question
    quiz_embed = discord.Embed(title="Quiz Time! 🎓", description=question, color=discord.Color.blurple())
    quiz_embed.add_field(name="A", value=choice_a, inline=False)
    quiz_embed.add_field(name="B", value=choice_b, inline=False)
    quiz_embed.add_field(name="C", value=choice_c, inline=False)
    quiz_embed.add_field(name="D", value=choice_d, inline=False)
    quiz_embed.set_footer(text="Click a button to answer!")

    # Create interactive buttons
    class QuizView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)

        @discord.ui.button(label="A", style=discord.ButtonStyle.red)
        async def button_a(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.process_answer(interaction, "A")

        @discord.ui.button(label="B", style=discord.ButtonStyle.blurple)
        async def button_b(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.process_answer(interaction, "B")

        @discord.ui.button(label="C", style=discord.ButtonStyle.green)
        async def button_c(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.process_answer(interaction, "C")

        @discord.ui.button(label="D", style=discord.ButtonStyle.gray)
        async def button_d(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.process_answer(interaction, "D")

        async def process_answer(self, interaction: discord.Interaction, choice):
            if choice == correct_answer:
                await interaction.response.send_message(f"**Correct!** {interaction.user.mention} chose the right answer!", ephemeral=True)
            else:
                await interaction.response.send_message(f"**Incorrect!** The correct answer was **{correct_answer}**.", ephemeral=True)

            # Disable buttons after an answer is selected
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)

    # Send the quiz question
    await interaction.followup.send(embed=quiz_embed, view=QuizView())

async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())