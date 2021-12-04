import discord 
from discord.ext import commands, tasks
import datetime
import random
import asyncio
from pymongo import MongoClient
from discord_components import Button, ButtonStyle, Select, SelectOption, Interaction, component

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
leveling = cluster['MysticBot']['levels']
profile = cluster['Economy']['economy-profile']
imoc = cluster['Economy']['economy-in_middle_of_command']
global_multi = cluster['Economy']['economy-GLOBAL']
ecoinv = cluster['Economy']['economy-inventory']
hourly_cd = cluster['Economy']['economy-hourly_cd'] 
daily_cd = cluster['Economy']['economy-daily_cd']
lottery_list = cluster['Economy']['economy-lottery_list']
lottery_timing = cluster['Economy']['economy-lottery_timing']

#currency 
coin_emoji = '🪙'

#embed specifications
embed_color = 0x2a72f7

# Emoji Config with DB
lotteryTicket = "<:lottery_ticket:915217769379807232> lottery ticket"

#Shop items
shop_items = f"""<:lottery_ticket:915217769379807232> `Lottery ticket` - allows you to join `lottery` | **1,000** {coin_emoji}\n"""

class EcoShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        pass
        self.lottery_system.start()
    
    @tasks.loop(seconds=10)
    async def lottery_system(self):
        time_now = datetime.datetime.utcnow()
        end_time = lottery_timing.find_one({"_id": 1})["end_time"]
        if time_now >= end_time:
            await asyncio.create_task(self.lotterSystem())
                

    
    async def lotterSystem(self):
        lot_list = lottery_list.find({})

        guild = self.bot.get_guild(705513318747602944)
        channel = guild.get_channel(875427665463611442)
        count = lottery_list.count_documents({}) # number of people joined the lottery

        if count >= 1:
            members = []
            for x in lot_list:
                member_id = x['_id']
                members.append(member_id) # add the members id to a empty list

            winner_id = random.choice(members) # randomly choose a id from members list
            winner_member = guild.get_member(winner_id)
            winning_coins = ((len(members)*(1000+random.randint(10,101)))*3)//2 

            update_wallet_coins(winner_member.id, winning_coins)

            for ids in members:
                ecoinv.update_one({"_id": ids}, {"$unset":{lotteryTicket:1}}) # update the members lottery ticket in inventory

            embed = discord.Embed(color=embed_color, timestamp=datetime.datetime.utcnow())
            embed.add_field(name=f"{coin_emoji} Lottery Winner 🎉", value=f"{winner_member.name} has won {winning_coins:,} {coin_emoji}")
            embed.set_footer(text=f"Total members joined {count}")
            await channel.send(embed=embed)
            
            next_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            lottery_timing.update_one({"_id": 1}, {"$set": {"end_time": next_time}}) # update next lottery time
            lottery_timing.update_one({"_id": 1}, {"$set": {"winner_id": winner_id}}) # update winner's ID 
            lottery_timing.update_one({"_id": 1}, {"$set": {"winner_reward": winning_coins}})

            lottery_list.delete_many({})  # remove all members who joined lottery
        else:
            next_time = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
            await channel.send("**Lottery event postponed for next 6 hours as no one joined it :(**")
            lottery_timing.update_one({"_id": 1}, {"$set": {"end_time": next_time}})
    

    @commands.command()
    async def shop(self, ctx, page:int=1):
        stats = profile.find_one({"_id": ctx.author.id})
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)
        
        embed = discord.Embed(description="**Buy items with `;buy [item]`**", color=embed_color)
        embed.add_field(name="Shop", value=shop_items)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def buy(self, ctx, *,item:str):
        stats = profile.find_one({"_id": ctx.author.id})
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)
        
        if item.lower() == "lottery ticket":
            old_wallet = stats['wallet']
            if old_wallet < 1000:
                return await ctx.send(f"**{ctx.author.name}** you don't have enough money to buy this item!")

            inventory = ecoinv.find_one({"_id": ctx.author.id})
            lot_list = lottery_list.find_one({"_id": ctx.author.id})
            if inventory is None:
                ecoinv.insert_one({"_id": ctx.author.id, lotteryTicket: 1})
                lottery_list.insert_one({"_id":ctx.author.id})
                update_wallet_coins(ctx.author.id, -1000)
                await ctx.send("**{}** enrolled you for the next lottery event".format(ctx.author.name))

            else:
                try:
                    lot_in_inv = inventory[lotteryTicket]
                except:
                    lot_in_inv = 0
                
                if lot_in_inv ==0:
                    ecoinv.update_one({"_id": ctx.author.id}, {"$set": {lotteryTicket: 1}})
                    lottery_list.insert_one({"_id":ctx.author.id})
                    update_wallet_coins(ctx.author.id, -1000)
                    await ctx.send("**{}** enrolled you for the next lottery event".format(ctx.author.name))

                elif lot_in_inv == 1:
                    return await ctx.send(f"**{ctx.author.name}** you already have a lottery ticket!")
    

    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.author
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        
        imoc_check2 = find_imoc(user.id)
        if imoc_check is False:
            if user == ctx.author:
                return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
            else:
                return await ctx.send(f"{ctx.author.mention} you can't do this {user.name} is in middle of a command")
        stats = profile.find_one({"_id": ctx.author.id})
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)
        invents = ecoinv.find_one({"_id": user.id})
        if invents is None:
            ecoinv.insert_one({"_id": user.id})

        item_list = []
        item_count = []
        for key in invents:
            item_list.append(f"{key}")
            item_count.append(invents[key])
        
        item_list.pop(0)
        item_count.pop(0)
        embed = discord.Embed(color = embed_color)
        embed.set_author(name=f"{user.name}'s inventory", icon_url=user.avatar_url)
        if len(item_list) >= 1:
            i = 0
            items = ""
            for x in item_list:
                items += f"**{item_list[i]}** {item_count[i]}\n"
                i += 1

            embed.add_field(name="Items", value=items, inline=True)

            await ctx.send(embed=embed)
        
        else:
            embed.add_field(name="Items", value="Nothing to see here :(", inline=False)
            await ctx.send(embed=embed)

    @commands.command()
    async def event(self, ctx):
        stats = profile.find_one({"_id": ctx.author.id})
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)

        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")

        lot_time = lottery_timing.find_one({"_id": 1})
        end_cd = lot_time['end_time']
        if end_cd < datetime.datetime.utcnow():
            return
        else:
            remaing_time = end_cd - datetime.datetime.utcnow()
            hours , reminder = divmod(int(remaing_time.total_seconds()), 60*60)
            minutes, seconds = divmod(int(reminder), 60)
        
            embed = discord.Embed(description=f"Lottery Event in ~-~ **{hours}h {minutes}m {seconds}s**", color= embed_color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)


    @commands.command()
    async def lottery(self, ctx):
        stats = profile.find_one({"_id": ctx.author.id})
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")

        lot_time = lottery_timing.find_one({"_id": 1}) # getting lottery remaining time
        end_cd = lot_time['end_time']
        if end_cd < datetime.datetime.utcnow():
            return
        else:
            remaing_time = end_cd - datetime.datetime.utcnow()
            hours , reminder = divmod(int(remaing_time.total_seconds()), 60*60)
            minutes, seconds = divmod(int(reminder), 60)

        index = lottery_timing.find_one({"_id": 1}) # get last winner and reward
        winner_id, winner_money = index['winner_id'], index['winner_reward']
        if (winner_id or winner_money) is None:
            winner_id, winner_money = self.bot.id, 69
        member = ctx.guild.get_member(winner_id)
        
        total_members = lottery_list.count_documents({}) # get all the members who joined lottery

        next_reward = ((total_members*(1000+random.randint(10,101)))*3)//2
        next_lottery = f"**Next Lottery:** {hours}h {minutes}m {seconds}s"
        current_pot = f"**Current Pot:** {next_reward} {coin_emoji}"
        last_winner = f"**Last Winner:** {member.name} ~-~ {winner_money} {coin_emoji}"

        embed = discord.Embed(description=f"{next_lottery}\n{current_pot}\n{last_winner}", color = 0xff0000)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(EcoShop(bot))


def find_imoc(player_id):
    index = imoc.find_one({"_id": player_id})
    if index is None:
        return True
    else:
        return False

def insert_imoc(player_id):
    imoc.insert_one({"_id": player_id})

def delete_imoc(player_id):
    imoc.delete_one({"_id": player_id})


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
    embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)
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


def beg_cooldown(ctx, beg):
    if beg.is_on_cooldown(ctx):
        minutes, seconds= divmod(int(beg.get_cooldown_retry_after(ctx)), 60) 
        time = f"🕐 ~-~ `Beg` (**{minutes}m {seconds}s**)"
    else:
        time = f"✅ ~-~ `Beg` "
    return time


def get_earning_cd(ctx, command, x):
    if command.is_on_cooldown(ctx):
        minutes, seconds= divmod(int(command.get_cooldown_retry_after(ctx)), 60) 
        time = f"🕐 ~-~ `{x.capitalize()}` (**{minutes}m {seconds}s**)"
    else:
        time = f"✅ ~-~ `{x.capitalize()}`"
    return time


def get_emoji():
    emojis_l = []
    while True:
        random_emoji = random.choice(emoji_list)
        emojis_l.append(random_emoji)
        if len(emojis_l) == 5:
            break
    emojis = "".join(emojis_l)
    return emojis

def slots_calulate(emojis):
    win = 0
    lose = 0
    for emoji in emojis:
        if emoji in ["🔥","🍀","✨", "💎",]:
            win += 1
        elif emoji in ["☘️","⚡","💯","🎁","🪙"]:
            lose += 1
    
    if win > lose:
        return True
    else:
        return False


def get_hourly_cd(player_id):
    command_cd = hourly_cd.find_one({"_id": player_id})
    if command_cd != None:
        end_cd = command_cd['hr_cd']
        hr_cd = end_cd - datetime.datetime.utcnow()
        minutes, seconds = divmod(int(hr_cd.total_seconds()), 60)
        time = f"🕐 ~-~ `Hourly` (**{minutes}m {seconds}s**)"
    else:
        time = f"✅ ~-~ `Hourly` "
    return time


def get_daily_cd(player_id):
    command_cd = daily_cd.find_one({"_id": player_id})
    if command_cd != None:
        end_cd = command_cd['daily_cd']
        dy_cd = end_cd - datetime.datetime.utcnow()
        hours, reminder = divmod(int(dy_cd.total_seconds()), 60*60)
        minutes, seconds = divmod(reminder, 60)
        time = f"🕐 ~-~ `Daily` (**{hours}h {minutes}m {seconds}s**)"
    else:
        time = "✅ ~-~ `Daily`"
    return time
        


def get_hourly_rewards(level):
    if level in range(1,11):
        reward = 100
    elif level in range(11,21):
        reward = 200
    elif level in range(21,41):
        reward = 400
    elif level in range(41,81):
        reward = 800
    elif level in range(81, 121):
        reward = 1200
    elif level in range(121, 181):
        reward = 2000
    elif level >= 181:
        reward = 5000
    return reward


def get_daily_rewards(level):
    if level in range(1,11):
        reward = 200
    elif level in range(11,21):
        reward = 400
    elif level in range(21,41):
        reward = 800
    elif level in range(41,81):
        reward = 1200
    elif level in range(81, 121):
        reward = 2400
    elif level in range(121, 181):
        reward = 5000
    elif level >= 181:
        reward = 10000
    return reward


def update_daily_streak(ctx, level, daily_streak, claim_now, last_claim):
    delta = claim_now - last_claim
    if delta > datetime.timedelta(hours=48):
        new_streak = 0
        daily_streak = new_streak
    else:
        if daily_streak < 7:
            daily_streak +=1
        elif daily_streak == 7:
            daily_streak = 7
    profile.update_one({"_id": ctx.author.id}, {"$set": {"daily_streak": daily_streak}})
    now = datetime.datetime.utcnow()
    profile.update_one({"_id": ctx.author.id}, {"$set": {"last_claim": now}})
    return daily_streak


def get_daily_streak_bonus(ctx, level, total_streak):
    multiplier = 1 + total_streak
    bonus = (level*multiplier) + 100 + random.randint(1,level)
    return bonus


def get_user_rank(ctx, level):
    if level in range(1,5):
        rank = ctx.guild.get_role(794886884497031168)
    elif level in range(5,10):
        rank = ctx.guild.get_role(794896587943575563)
    elif level in range(10,20):
        rank = ctx.guild.get_role(794896588623052830)
    elif level in range(20,40):
        rank = ctx.guild.get_role(794896601856475166)
    elif level in range(40,80):
        rank = ctx.guild.get_role(794896602694156318)
    elif level in range(80, 120):
        rank = ctx.guild.get_role(794896707971973132)
    elif level in range(120, 150):
        rank = ctx.guild.get_role(794896709238784011)
    elif level in range(150, 180):
        rank = ctx.guild.get_role(796353896478015549)
    elif level in range(180, 200):
        rank = ctx.guild.get_role(796354367711870997)
    elif level >= 200:
        rank = ctx.guild.get_role(794896709380866098)
    else:
        rank = None
    return rank


def update_wallet_coins(player_id, money):
    stats = profile.find_one({"_id": player_id})
    old_wallet = stats['wallet']
    new_wallet = old_wallet + money
    profile.update_one({"_id": player_id}, {"$set": {"wallet": new_wallet}})