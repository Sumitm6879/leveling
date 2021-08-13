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
bot = commands.Bot(command_prefix=get_prefix(),
                   intents=intents)
bot.remove_command('help')

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
bot_prefix = cluster['MysticBot']['bot_prefix']
print("DB CONNECTED")


def get_prefix():
    stats = bot_prefix.find_one({"_id": bot.user.id})
    if stats is None:
        prefix = ';;'
    else:
        prefix = stats['prefix']
        return prefix


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


@bot.command()
async def set_prefix(ctx, *, prefix: str):
    stats = bot_prefix.find_one({"_id": bot.user.id})
    old_prefix = stats['prefix']
    await ctx.send(f"The old preix was {old_prefix}\nEnter the new Prefix length should be less then 3 characters!\nTimeout in `15 seconds`")
    try:
        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id
        msg = await bot.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send("Timeout Try again!")
    else:
        if len(msg.content) < 3:
            new_prefix = msg.content
            bot_prefix.update_one({"_id":bot.user.id}, {"$set":{"prefix":new_prefix}})
            await ctx.send(f"set the new prefix of bot as `{new_prefix}`")
        else:
            await ctx.send("Operation Failed Try again!")
            
            
    
@bot.command()
async def ping(ctx):
    numbers = {0: '𝟘', 1: '𝟙', 2: '𝟚', 3: '𝟛', 4: '𝟜', 5: '𝟝', 6: '𝟞', 7: '𝟟', 8: '𝟠', 9: '𝟡'}
    ping = round(bot.latency * 1000)
    x = [int(a) for a in str(ping)]
    new_ping = ""
    for i in x:
        new_ping += "".join(numbers[i])

    embed = discord.Embed(title="Mystic Levels's Latency", description=f'**{new_ping} 𝕞𝕤**', color=0xff0000)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f"{bot.command_prefix}help to get more info.", icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)
    

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
