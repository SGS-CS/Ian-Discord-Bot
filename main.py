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
    quiz_name="The name of the quiz",
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
async def createquestion(interaction: discord.Interaction, quiz_name: str, question: str, choice_a: str, choice_b: str, choice_c: str, choice_d: str, correct_answer: str):
    
    user_name = interaction.user.name  # Store the username instead of user ID

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO questions (quiz_name, user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (quiz_name, user_name, question, choice_a, choice_b, choice_c, choice_d, correct_answer))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()

    await interaction.response.send_message(
        f"**Question added to '{quiz_name}'!**\n"
        f"**Question ID:** `{question_id}`\n\n"
        f"**Q:** {question}\n"
        f"**A:** {choice_a}\n"
        f"**B:** {choice_b}\n"
        f"**C:** {choice_c}\n"
        f"**D:** {choice_d}\n"
        f"**Correct Answer:** {correct_answer}",
        ephemeral=True
    )
@bot.tree.command(name="runquiz", description="Start a quiz session")
@discord.app_commands.describe(
    quiz_name="The name of the quiz to run (leave empty if running a single question)",
    question_id="ID of a specific question to run (leave empty if running a quiz)"
)
async def runquiz(interaction: discord.Interaction, quiz_name: str = None, question_id: int = None):
    user_name = interaction.user.name  # Compare using username instead of numeric ID
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    if question_id:
        # Fetch a specific question by ID
        cursor.execute("SELECT user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice FROM questions WHERE id = ?", (question_id,))
        question_data = cursor.fetchone()
        if question_data:
            questions = [question_data]  # Put it in a list for consistency
        else:
            questions = []
    elif quiz_name:
        # Fetch all questions from the given quiz, shuffled
        cursor.execute("SELECT user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice FROM questions WHERE quiz_name = ? ORDER BY RANDOM()", (quiz_name,))
        questions = cursor.fetchall()
    else:
        await interaction.response.send_message("Please provide either a quiz name or a question ID.", ephemeral=True)
        return

    conn.close()

    if not questions:
        await interaction.response.send_message("No questions found or you don't have permission.", ephemeral=True)
        return

    # Ensure only the creator can run the quiz
    creator_name = questions[0][0]
    if creator_name != user_name:
        await interaction.response.send_message("You are not the creator of this quiz!", ephemeral=True)
        return

    await interaction.response.send_message(f"Starting quiz **'{quiz_name}'**! Get ready...", ephemeral=True)

    # Loop through all questions
    for question_data in questions:
        _, question, choice_a, choice_b, choice_c, choice_d, correct_answer = question_data

        quiz_embed = discord.Embed(title="Question:", description=question, color=discord.Color.blurple())
        quiz_embed.add_field(name="A", value=choice_a, inline=False)
        quiz_embed.add_field(name="B", value=choice_b, inline=False)
        quiz_embed.add_field(name="C", value=choice_c, inline=False)
        quiz_embed.add_field(name="D", value=choice_d, inline=False)
        quiz_embed.set_footer(text="Click a button to answer!")

        class QuizView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.answered = False

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
                if self.answered:
                    return  # Ignore multiple clicks
                self.answered = True

                if choice == correct_answer:
                    await interaction.response.send_message(f"**Correct!** {interaction.user.mention} chose the right answer!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"**Incorrect!** The correct answer was **{correct_answer}**.", ephemeral=True)

                # Disable buttons after an answer is selected
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(view=self)

        await interaction.followup.send(embed=quiz_embed, view=QuizView())
        await asyncio.sleep()  # Short delay before the next question

async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())