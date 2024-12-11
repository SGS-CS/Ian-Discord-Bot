import discord
from discord.ext import commands

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online")
    
    # Prefix Commands
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello there, {ctx.author.mention}!")

    @commands.command(aliases=["gm", "morning"])
    async def goodmorning(self, ctx):
        await ctx.send(f"Good morning, {ctx.author.mention}!")

    # Prefix Commands w/ Embeds
    @commands.command()
    async def sendembed(self, ctx):
        embeded_msg = discord.Embed(title="Title of embed", description="Description of embed", color=discord.Color.green())
        embeded_msg.set_author(name="Footer text", icon_url=ctx.author.avatar)
        embeded_msg.set_thumbnail(url=ctx.author.avatar)
        embeded_msg.add_field(name="Name of field", value="Value of field", inline=False)
        embeded_msg.set_image(url=ctx.guild.icon)
        embeded_msg.set_footer(text="Footer text", icon_url=ctx.author.avatar)
        await ctx.send(embed=embeded_msg)

    @commands.command()
    async def ping(self, ctx):
        ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blue())
        ping_embed.add_field(name=f"{self.bot.user.name}'s Latency (ms): ", value=f"{round(self.bot.latency*1000)}ms.", inline=False)
        ping_embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.avatar)
        await ctx.send(embed=ping_embed)

async def setup(bot):
    await bot.add_cog(Prefix(bot))