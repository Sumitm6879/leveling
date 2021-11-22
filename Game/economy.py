import datetime
import discord
import random
from discord.ext import commands
from pymongo import MongoClient

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
leveling = cluster['MysticBot']['levels']
profile = cluster['Economy']['economy-profile']

#embed specifications
embed_color = 0x2a72f7

#beg choice
failed_beg_choice = [
    "Lmao you didn't find anyone",
    "you broke? badluck!",
    "No Begging in the server you wanna get mute?",
    "You looked around but there are no people around"]



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
    
    @commands.command(aliases=['bal', 'profile'])
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
        else:
            if member == ctx.author:
                await ctx.send(f"**{member.name}** new to this? consider `;start` to get started")
            elif member.bot:
                await ctx.send("You cannot check balance of a bot")
            elif member != ctx.author:
                await ctx.send(f"**{member.name}** has never played")


    @commands.command()
    async def deposit(self, ctx, money:str):
        search = player_search(ctx.author.id)
        stats = profile.find_one({"_id": ctx.author.id})
        if search:
            if money == "all":
                money = stats['wallet']
            else:
                money = convert_str_to_number(money)
            if isinstance(money, int):
                old_wallet = stats['wallet']
                if money <= old_wallet:
                    new_wallet = old_wallet-money
                    new_bank = stats['bank'] + money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet": new_wallet}})
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"bank": new_bank}})
                    await ctx.send(f"**{ctx.author.name}** deposited 🪙 **{money}**")
                else:
                    return await ctx.send("Check your wallet **{ctx.author.name}** Lmao!")
            else:
                return await ctx.send(f"**{ctx.author.name}** please enter a valid amount!")
        else:
            await ctx.send(f"**{ctx.author.name}** new to this? consider `;start` to get started")

            
    @commands.command()
    async def withdraw(self, ctx, money:str):
        search = player_search(ctx.author.id)
        stats = profile.find_one({"_id": ctx.author.id})
        if search:
            if money.lower() == "all":
                money = stats['bank']
            else:
                money = convert_str_to_number(money)
            if isinstance(money, int):
                old_bank = stats['bank']
                if money <= old_bank:
                    new_wallet = stats['wallet'] + money
                    new_bank = stats['bank'] - money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet": new_wallet}})
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"bank": new_bank}})
                    await ctx.send(f"**{ctx.author.name}** 🪙 **{money}** withdrawn")
                else:
                    return await ctx.send("**{ctx.author.name}** duh! check your bank and try again")
            else:
                return await ctx.send(f"**{ctx.author.name}** please enter a valid amount!")
        else:
            await ctx.send(f"**{ctx.author.name}** new to this? consider `;start` to get started")
        

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def beg(self, ctx):
        search = player_search(ctx.author.id)
        if search:
            chance1 = random.randint(1,11)
            if chance1 in range(3,8):
                index = leveling.find_one({"_id": ctx.author.id})
                stats = profile.find_one({"_id": ctx.author.id})
                if index is None:
                    failed_sentence = random.choice(failed_beg_choice)
                    return await ctx.send(f"{failed_sentence}")
                xp = index['xp']
                level = calculate_level(xp)
                beg_money = level*(random.randint(1,3))+random.randint(45,101)
                new_wallet = stats['wallet'] + beg_money
                profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet":new_wallet}})
                await ctx.send(f"**{ctx.author.name}** you earned 🪙**{new_wallet}**")
            else:
                failed_sentence = random.choice(failed_beg_choice)
                await ctx.send(f"**{ctx.author.name}** {failed_sentence}")
        else:
            welcm = new_to_this(ctx)
            await ctx.send(welcm)

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title=f"Cooldown!",description=f"Try again in **{error.retry_after:.2f}s**.", color=embed_color)
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Economy(bot))

def player_search(player_id):
    player = profile.find_one({"_id": player_id})
    if player:
        return True
    else:
        return False

def balance_embed(member, wallet, bank):
    wallet, bank= "{:,}".format(wallet), "{:,}".format(bank)
    embed = discord.Embed(
        title = "Balance",
        description = f"🪙 **Wallet:** {wallet}\n🏦 **Bank:** {bank}",
        color = embed_color,
        timestamp = datetime.datetime.utcnow())
    embed.set_author(name=f"{member.name}", url=member.avatar_url)
    embed.set_thumbnail(url=member.avatar_url)
    return embed

def calculate_level(xp):
    lvl = 0
    while True:
        if xp < ((20 * (lvl ** 2)) + (20 * lvl)):
            break
        lvl += 1
    return lvl

def convert_str_to_number(no):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000, 'T':1000000000000}
    if no.isdigit():
        total_stars = int(no)
    else:
        if len(no) > 1:
            total_stars = float(no[:-1]) * num_map.get(no[-1].upper(), 1)
    return int(total_stars)

def new_to_this(ctx):
    tada = f"**{ctx.author.name}** new to this? consider `;start` to get started"
    return tada