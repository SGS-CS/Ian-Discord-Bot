# Import all required libraries/packages
import sqlite3
import discord
from discord.ext import commands

# This cog handles the database setup
class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Store the bot instance
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online") # Runs when the bot successfully connects to Discord

    # Connect to the SQLite database (and create a database if quiz.db doesn't exist)
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    # Create a table to store quiz questions if it doesn't already exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_name TEXT NOT NULL,
        user_id TEXT NOT NULL,  -- Changed from INTEGER to TEXT
        question TEXT NOT NULL,
        choice_a TEXT NOT NULL,
        choice_b TEXT NOT NULL,
        choice_c TEXT NOT NULL,
        choice_d TEXT NOT NULL,
        correct_choice TEXT NOT NULL
    )
    """)

async def setup(bot):
    await bot.add_cog(Database(bot)) # Adds this cog to the bot