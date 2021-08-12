from datetime import datetime
from os import name
import discord
from discord import client
from discord.ext import commands
import datetime
from discord.ext.commands import CommandNotFound, MemberNotFound, MissingPermissions, MissingRequiredArgument, \
    BadArgument, CommandOnCooldown
from pymongo import MongoClient
import mleveling

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=';;',
                   intents=intents)
bot.remove_command('help')

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
print("DB CONNECTED")

cogs = [mleveling]

for i in range(len(cogs)):
    cogs[i].setup(bot)
    print("yay!!")


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(type=discord.ActivityType.listening, name='>> Mystic help <<'))
    print("Logged in as: " + bot.user.name + "\n")
    chan = bot.get_channel(721361976957206568)
    await chan.send("Leveling Bot ONline")


@bot.command(aliases=['h', 'H', 'HELP', 'Help', 'HElp'])
async def help(ctx, arg: str = None):
    if arg is None:
        embed = discord.Embed(
            title='Mystic Leveling System',
            description='Everyone Gets **1xp** per message\nServer boosters Get **2xp** per message',
            color=0xff0000,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name='Commands', value='🔻🔻🔻🔻', inline=False)
        embed.add_field(name=f"{bot.command_prefix}level", value="Shows your level\n**Aliases**\n> `lvl`, `rank`", inline=False)
        embed.add_field(name=f"{bot.command_prefix}leaderboard", value="Shows server Leaderboard\n**Aliases**\n> "
                                                                       "`lb`, `top`", inline=False)
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    elif arg.lower() == 'staff':
        embed = discord.Embed(
            title='Mystic Leveling System',
            description='Everyone Gets **1xp** per message\nServer boosters Get **2xp** per message',
            color=0xff0000,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name='Staff Commands', value='🔻🔻🔻🔻', inline=False)
        embed.add_field(name=f'{bot.command_prefix}add-xp [member] [amount]',
                        value='> Adds amount xp to member\n> Requires Kick members permission', inline=False)
        embed.add_field(name=f'{bot.command_prefix}rev-xp [member] [amount]',
                        value='> Removes amount xp from member\n> Requires Kick members permission', inline=False)
        embed.add_field(name=f'{bot.command_prefix}set level [member] [level]',
                        value='> changes the level of member\n> Requires Kick members permission', inline=False)
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        pass
    elif isinstance(error, MissingPermissions):
        await ctx.send(f"**ERROR 403 FORBIDDEN**\n> {error}")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(f"**ERROR 400 BAD REQUEST**\n> {error}")
    elif isinstance(error, MemberNotFound):
        await ctx.send(f"**ERROR 404**\n> {error}")
    elif isinstance(error, BadArgument):
        await ctx.send(f"**ERROR 400 BAD REQUEST**\n> {error}")
    else:
        raise error


bot.run('ODc0MjcyOTUxMDQ0ODI1MTU4.YREkIg.GFJRkzHCxBvHgUJvJjZysvZikKk')
