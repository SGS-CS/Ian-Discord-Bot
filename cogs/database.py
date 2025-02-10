import sqlite3
import discord
from discord.ext import commands

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online")

    # Connects to the database
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    # Creates a table for storing quiz questions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        choice_a TEXT NOT NULL,
        choice_b TEXT NOT NULL,
        choice_c TEXT NOT NULL,
        choice_d TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

async def setup(bot):
    await bot.add_cog(Database(bot))