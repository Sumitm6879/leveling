import datetime
from os import name
from typing import Text
import discord
from discord.ext import commands
from pymongo import MongoClient

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
leveling = cluster['MysticBot']['levels']
profile = cluster['Economy']['economy-profile']

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy Ready!")
    
    @commands.command()
    async def start(self, ctx):
        stats = profile.find_one({"_id":ctx.author.id})
        if stats is None:
            new_player = {"_id":ctx.author.id, "wallet":100, "bank":0}
            profile.insert_one(new_player)
            await ctx.send(f"You are all set **{ctx.author.name}**")
        else:
            return
    
    @commands.command()
    async def balance(self, ctx, member: discord.Member=None):
        if member is None and ctx.message.reference:
            msg = await ctx.channel.fetch_message(id=ctx.message.reference.message_id)
            member = msg.author
        if member is None:
            member = ctx.author
        search = player_search(member.id)
        if search:
            stats = profile.find_one({"_id": member.id})
            wallet, bank = stats['wallet'], stats['bank']
            embed = balance_embed(member, wallet, bank)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))

def player_search(player_id):
    player = profile.find_one({"_id": player_id})
    if player:
        return True
    else:
        return False

def balance_embed(member, wallet, bank):
    embed = discord.Embed(
        title = "Balance",
        description = "**Wallet:** {wallet}\n**Bank:** {bank}",
        color = 0x2a72f7,
        timestamp = datetime.datetime.utcnow())
    embed.set_author(name=f"{member.name}", url=member.avatar_url)
    embed.set_thumbnail(url=member.avatar_url)
    return embed
