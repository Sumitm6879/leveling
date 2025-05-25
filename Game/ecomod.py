import datetime
from os import name
from typing import Text
import discord
from discord.ext import commands
from pymongo import MongoClient

P = 'password'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
leveling = cluster['MysticBot']['levels']
profile = cluster['Economy']['economy-profile']
lottery_timing = cluster['Economy']['economy-lottery_timing']

class EcoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, user:discord.Member):
        if ctx.author.id == 786862562494251038:
            stats = profile.find_one({"_id": user.id})
            if stats is None:
                return await ctx.send(f"**{user.name}** has never played")
            else:
                profile.delete_one({"_id": user.id})
                await ctx.send(f"Removed {user.name} from game all data wiped out")

    @commands.command()
    async def startLottery(self, ctx, user:discord.Member):
        if ctx.author.id == 786862562494251038:
            now  = datetime.datetime.utcnow()
            end_time = datetime.timedelta(minutes=2)
            lottery_end_time = now + end_time
            lottery_timing.update_one({"_id": 1}, {"$set": {"end_time": lottery_end_time}})
            await ctx.send("started lottery!")
            

def setup(bot):
    bot.add_cog(EcoMod(bot))
