# Import all required libraries/packages
import discord
from discord.ext import commands

import os
import asyncio
import sqlite3

# Create a bot instance with the prefix "." and enable all intents
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    # Runs when the bot successfully connects to Discord
    print("bot is online")
    await bot.change_presence(activity=discord.Game(name='/help')) # Set bot's status
    try:
        synced_commands = await bot.tree.sync() # Sync application commands (slash commands)
        print(f"Synced {len(synced_commands)} command(s).")
    except Exception as e:
        print("An error with syncing application commands has occured: ", e)

# Read the bot token from a file (security measure to avoid hardcoding it)
with open("token.txt") as file:
    token = file.read()

# Function to load cogs(files) from the "cogs" folder
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"): # Only load Python files
            print(f"Attempting to load extension: {filename}")
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}") # Remove .py before outputting debug message
                print(f"Successfully loaded: {filename}")
            except Exception as e:
                print(f"Failed to load: {filename}\nError: {e}")

# A dropdown menu to choose quiz modes(prototype)
class SelectMenu(discord.ui.View):
    options = [
        discord.SelectOption(label="Flashcards", value="1", description="Study individually with flashcards."),
        discord.SelectOption(label="Solo Quiz", value="2", description="Study individually with multiple-choice questions."),
        discord.SelectOption(label="Team Quiz", value="3", description="Study in a group with multiple-choice questions.")
    ]

    @discord.ui.select(placeholder="Select Mode:", options=options)
    async def menu_callback(self, interaction: discord.Interaction, select):
        select.disabled=True # Disable the dropdown after selection
        if select.values[0] == "1":
            await interaction.response.send_message(content="You chose to play Flashcards.")
        elif select.values[0] == "2":
            await interaction.response.send_message(content="You chose to play Solo Quiz.")
        elif select.values[0] == "3":
            await interaction.response.send_message(content="You chose to play Team Quiz.")

# Slash command to open the quiz mode selection menu(prototype)
@bot.tree.command(name="choosemode", description="Choose the mode you wish to play(Prototype)")
async def choosemode(interaction: discord.Interaction):
    await interaction.response.send_message(content="Choose the mode you wish to play", view=SelectMenu())

# Slash command to create a new quiz question and store it in the database
@bot.tree.command(name="createquestion", description="Add a question to a quiz(Working Feature)")
@discord.app_commands.describe(
    quiz_name="The name of the quiz",
    question="The quiz question",
    choice_a="Option A",
    choice_b="Option B",
    choice_c="Option C",
    choice_d="Option D",
    correct_answer="The correct answer (A, B, C, or D)",
    image_url="Optional image URL for the question"
)
@discord.app_commands.choices(correct_answer=[
    discord.app_commands.Choice(name="A", value="A"),
    discord.app_commands.Choice(name="B", value="B"),
    discord.app_commands.Choice(name="C", value="C"),
    discord.app_commands.Choice(name="D", value="D"),
])
async def createquestion(interaction: discord.Interaction, quiz_name: str, question: str, choice_a: str, choice_b: str, choice_c: str, choice_d: str, correct_answer: str, image_url: str = None):
    user_name = interaction.user.name
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    # Ensure the image_url column exists (one-time safety check)
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN image_url TEXT")
    except:
        pass  # Ignore if it already exists

    cursor.execute("""
    INSERT INTO questions (quiz_name, user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (quiz_name, user_name, question, choice_a, choice_b, choice_c, choice_d, correct_answer, image_url))
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
        f"**Correct Answer:** {correct_answer}\n"
        f"**Image URL:** {image_url or 'None'}",
        ephemeral=True
    )
    
# Slash command to start a quiz session
@bot.tree.command(name="runquiz", description="Start a quiz session(Working Feature)")
@discord.app_commands.describe(
    quiz_name="The name of the quiz to run (leave empty if running a single question)",
    question_id="ID of a specific question to run (leave empty if running a quiz)"
)
async def runquiz(interaction: discord.Interaction, quiz_name: str = None, question_id: int = None):
    user_name = interaction.user.name
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    if question_id:
        cursor.execute("SELECT user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice, image_url FROM questions WHERE id = ?", (question_id,))
        questions = [cursor.fetchone()]
    elif quiz_name:
        cursor.execute("SELECT user_id, question, choice_a, choice_b, choice_c, choice_d, correct_choice, image_url FROM questions WHERE quiz_name = ? ORDER BY RANDOM()", (quiz_name,))
        questions = cursor.fetchall()
    else:
        await interaction.response.send_message("Please provide either a quiz name or a question ID.", ephemeral=True)
        return

    conn.close()

    if not questions or questions[0] is None:
        await interaction.response.send_message("No questions found or you don't have permission.")
        return

    creator_name = questions[0][0]
    if creator_name != user_name:
        await interaction.response.send_message("You are not the creator of this quiz!")
        return

    if question_id:
        await interaction.response.send_message(f"Starting question ID: `{question_id}`! Get ready...")
    elif quiz_name:
        await interaction.response.send_message(f"Starting quiz **'{quiz_name}'**! Get ready...")


    for question_data in questions:
        _, question, a, b, c, d, correct_answer, image_url = question_data

        embed = discord.Embed(title="Question", description=question, color=discord.Color.blurple())
        embed.add_field(name="A", value=a, inline=False)
        embed.add_field(name="B", value=b, inline=False)
        embed.add_field(name="C", value=c, inline=False)
        embed.add_field(name="D", value=d, inline=False)
        embed.set_footer(text="Time remaining: 30s")

        if image_url:
            embed.set_image(url=image_url)

        view = discord.ui.View()
        answered = False

        async def button_callback(interaction: discord.Interaction, choice: str):
            nonlocal answered
            if answered:
                return
            answered = True
            if choice == correct_answer:
                await interaction.response.send_message(f"✅ Correct! {interaction.user.mention}")
            else:
                await interaction.response.send_message(f"❌ Incorrect! {interaction.user.mention} Correct answer: **{correct_answer}**")
            for item in view.children:
                item.disabled = True
            await message.edit(view=view)

        for label, style in zip(["A", "B", "C", "D"], [discord.ButtonStyle.red, discord.ButtonStyle.blurple, discord.ButtonStyle.green, discord.ButtonStyle.gray]):
            button = discord.ui.Button(label=label, style=style)
            button.callback = lambda i, choice=label: button_callback(i, choice)
            view.add_item(button)

        message = await interaction.followup.send(embed=embed, view=view, wait=True)

        for remaining in range(29, -1, -1):
            if answered:
                break
            embed.set_footer(text=f"Time remaining: {remaining}s")
            await message.edit(embed=embed)
            await asyncio.sleep(0.7)

        if not answered:
            await interaction.followup.send("⏰ Time's up! No answer was selected.")
            for item in view.children:
                item.disabled = True
            await message.edit(view=view)

        await asyncio.sleep(2)
async def main():
    async with bot:
        await load()
        await bot.start(token)

asyncio.run(main())