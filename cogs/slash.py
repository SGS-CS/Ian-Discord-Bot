import discord
from discord.ext import commands
from discord import app_commands

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online")

    # Slash Commands
    @app_commands.command(name="hello", description="Says hello to the person who ran the command")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{interaction.user.mention} Hello there!")

    @app_commands.command(name="goodmorning", description="Sends a good morning message")
    async def goodmorning(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Good morning, {interaction.user.mention}!")

    @app_commands.command(name="sendembed", description="Sends an embed message")
    async def sendembed(self, interaction: discord.Interaction):
        embeded_msg = discord.Embed(title="Title of embed", description="Description of embed", color=discord.Color.green())
        embeded_msg.set_author(name="Footer text", icon_url=interaction.user.avatar)
        embeded_msg.set_thumbnail(url=interaction.user.avatar)
        embeded_msg.add_field(name="Name of field", value="Value of field", inline=False)
        embeded_msg.set_image(url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None)
        embeded_msg.set_footer(text="Footer text", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embeded_msg)

    @app_commands.command(name="ping", description="Shows the bot's latency in ms")
    async def ping(self, interaction: discord.Interaction):
        ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency * 1000)}ms.", inline=False)
        ping_embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=ping_embed)

async def setup(bot):
    await bot.add_cog(Slash(bot))
