# Import all required libraries/packages
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

# This cog handles all of the bot's slash commands
class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Store the bot instance

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online") # Runs when the bot successfully connects to Discord

    # Slash command to send an embedded message (prototype)
    @app_commands.command(name="sendembed", description="Sends an embed message(Prototype)")
    async def sendembed(self, interaction: discord.Interaction):
        # Create an embed with a title, description, and color
        embeded_msg = discord.Embed(title="Title of embed", description="Description of embed", color=discord.Color.green())

        # Set the author and thumbnail to the command user's avatar
        embeded_msg.set_author(name="Footer text", icon_url=interaction.user.avatar)
        embeded_msg.set_thumbnail(url=interaction.user.avatar)

        # Add a field with placeholder content
        embeded_msg.add_field(name="Name of field", value="Value of field", inline=False)

        # Set an image (server icon if available)
        embeded_msg.set_image(url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None)
       
        # Set a footer
        embeded_msg.set_footer(text="Footer text", icon_url=interaction.user.avatar)
        
        # Send the embed message
        await interaction.response.send_message(embed=embeded_msg)

    # Slash command to check bot latency
    @app_commands.command(name="ping", description="Shows the bot's latency in ms(Working Feature)")
    async def ping(self, interaction: discord.Interaction):
        # Create an embed with the bot's latency
        ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency * 1000)}ms.", inline=False)

        # Set footer with requester info
        ping_embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
        
        # Send the latency information
        await interaction.response.send_message(embed=ping_embed)
    
    # Slash command to retrieve a quiz question by its ID
    @app_commands.command(name="getquestion", description="Retrieve a question by ID from the database (Working Feature)")
    async def getquestion(self, interaction: discord.Interaction, question_id: int):
        user_name = interaction.user.name  # Get the command user's username

        # Connect to the database
        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        # Fetch the question, quiz name, and creator's username
        cursor.execute("SELECT quiz_name, user_id, question, choice_a, choice_b, choice_c, choice_d FROM questions WHERE id=?", (question_id,))
        result = cursor.fetchone()
        conn.close()

        # If the question doesn't exist, inform the user
        if not result:
            await interaction.response.send_message(f"No question found with ID `{question_id}`.", ephemeral=True)
            return

        # Unpack the retrieved data
        quiz_name, creator_name, question, choice_a, choice_b, choice_c, choice_d = result

        # Only the creator can view their own question
        if creator_name != user_name:
            await interaction.response.send_message("You do not have permission to view this question.", ephemeral=True)
            return

        # Format the message
        response_message = (
            f"**Quiz Name:** `{quiz_name}`\n"
            f"**Question ID:** `{question_id}`\n"
            f"**Creator:** `{creator_name}`\n\n"
            f"**Question:** {question}\n\n"
            f"**Choice A:** {choice_a}\n"
            f"**Choice B:** {choice_b}\n"
            f"**Choice C:** {choice_c}\n"
            f"**Choice D:** {choice_d}"
        )

        # Send the formatted message
        await interaction.response.send_message(response_message, ephemeral=True)
    
    # Slash command to display the help menu
    @app_commands.command(name="help", description="Displays a list of all available commands and how to use them(Working Feature)")
    async def help(self, interaction: discord.Interaction):
        # Create an embed for the help message
        help_embed = discord.Embed(
            title="Help Menu - Quiz Bot",
            description="Here is a list of all the available commands and how to use them:",
            color=discord.Color.gold()
        )

        # Add fields for each command
        help_embed.add_field(
            name="📌 `/createquestion`",
            value="Creates a new quiz question.\n"
                  "**Usage:** `/createquestion quiz_name: <name> question: <text> choice_a: <A> choice_b: <B> choice_c: <C> choice_d: <D> correct_answer: <A/B/C/D>`",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/runquiz`",
            value="Starts a quiz session.\n"
                  "**Usage:** `/runquiz quiz_name: <name>` → Runs all questions in the quiz in random order.\n"
                  "**Usage:** `/runquiz question_id: <id>` → Runs a specific question by ID.",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/getquestion`",
            value="Retrieves a question by ID. Only the creator of the question can access it.\n"
                  "**Usage:** `/getquestion question_id: <id>`",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/choosemode`",
            value="Lets you choose how you want to play: Flashcards, Solo Quiz, or Team Quiz.\n"
                  "**Usage:** `/choosemode` → Opens a menu to select a mode.",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/ping`",
            value="Displays the bot’s latency in milliseconds.\n"
                  "**Usage:** `/ping`",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/sendembed`",
            value="Sends a prototype embed message (for testing).\n"
                  "**Usage:** `/sendembed`",
            inline=False
        )

        help_embed.add_field(
            name="📌 `/help`",
            value="Displays this help menu.\n"
                  "**Usage:** `/help`",
            inline=False
        )

        # Set footer and send message
        help_embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=help_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Slash(bot)) # Adds this cog to the bot

