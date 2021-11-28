import datetime
import discord
from functions import *
import random
from discord.ext import commands, tasks
from pymongo import MongoClient

P = 'sumitm6879sm'
cluster = MongoClient(
    f"mongodb+srv://{P}:sm6879sm@sambot.ipbu6.mongodb.net/SamBot?retryWrites=true&w=majority"
)
leveling = cluster['MysticBot']['levels']
profile = cluster['Economy']['economy-profile']
imoc = cluster['Economy']['economy-in_middle_of_command']
global_multi = cluster['Economy']['economy-GLOBAL']
hourly_cd = cluster['Economy']['economy-hourly_cd'] 
daily_cd = cluster['Economy']['economy-daily_cd']

#Globals specification
gM = global_multi.find_one({"_id": "globalMulti"})
globalMultiplier = gM['globalmultiplier']

#currency 
coin_emoji = '🪙'

#thumbnails
cf_head = "https://i.imgur.com/BvnksIe.png"
cf_tail = "https://i.imgur.com/i6XvztF.png"
cf_sides = "https://imgur.com/2l48T28"

#embed specifications
embed_color = 0x2a72f7

#beg choice
failed_beg_choice = [
    "Lmao you didn't find anyone",
    "you broke? badluck!",
    "No Begging in the server you wanna get mute?",
    "you looked around but there are no people to beg"]

#roam choices 
roam_choices = [
    "while roaming you found a wallet droped on the street",
    "you helped police in catching a thief",
    "you stole money from a kid! very bad",
    "a rich man walks up to you and was very pleased to talk to you",
    "you helped a thief escape!",
    "you stole your friends money!",
    "a drunk man was alseep on the bench **||you robed him||**",
    "you got into a street fight, You won!",
    "a blind man has lost his stick you helped him\nit was a tik tok video",
    "you helped clean the cleaner to pick up trash lying on the street",
    "you feel too lazy to walk so you returned home but you found your lost wallet in you pants ||it was never lost||",
    "while walking around the garden you found your lost money!"
]

# gamble emojis
emoji_list = ["🔥", "⚡", "✨", "💎", "🍀", "💯", "🎁", "🪙"]


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy Ready!")
        self.update_hr_cd.start()
        self.update_dy_cd.start()
    
    @tasks.loop(seconds=1)
    async def update_hr_cd(self):
        member_cd = hourly_cd.find({}).sort("date", 1)
        if member_cd != None:
            for x in member_cd:
                member_id, end_time = x['_id'], x['hr_cd']
                time_now = datetime.datetime.utcnow()
                if time_now >= end_time:
                    hourly_cd.delete_one({"_id": member_id})

    @tasks.loop(seconds=1)
    async def update_dy_cd(self):
        member_cd = daily_cd.find({}).sort("date", 1)
        if member_cd != None:
            for x in member_cd:
                member_id, end_time = x['_id'], x['daily_cd']
                time_now = datetime.datetime.utcnow()
                if time_now>= end_time:
                    daily_cd.delete_one({"_id": member_id})

    @commands.command()
    async def start(self, ctx):
        stats = profile.find_one({"_id":ctx.author.id})
        index = leveling.find_one({"_id": ctx.author.id})
        if stats is None and index:
            new_player = {"_id":ctx.author.id, "wallet":100, "bank":0}
            profile.insert_one(new_player)
            await ctx.send(f"You are all set **{ctx.author.name}**")
        else:
            return
    

    @commands.command(aliases=['bal', 'profile'])
    async def balance(self, ctx, member: discord.Member=None):
        if member != None and member.bot:
            return await ctx.send(f"This does not works for bots {ctx.author.mention}")
        if member is None and ctx.message.reference:
            msg = await ctx.channel.fetch_message(id=ctx.message.reference.message_id)
            member = msg.author
        if member is None:
            member = ctx.author
        search = player_search(member.id)
        imoc_check = find_imoc(member.id)
        if imoc_check is False:
            if member == ctx.author:
                return await ctx.send(f"{member.mention} you can't do this end your previous command!")
            else:
                return await ctx.send(f"{ctx.author.mention} you can't do this {member.name} is in a middle of command!")

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
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        if search:
            if money == "all":
                money = stats['wallet']
            else:
                money = convert_str_to_number(money)
            if isinstance(money, int):
                old_wallet = stats['wallet']
                if money <= old_wallet and money > 0:
                    new_wallet = old_wallet-money
                    new_bank = stats['bank'] + money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet": new_wallet}})
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"bank": new_bank}})
                    await ctx.send(f"**{ctx.author.name}** deposited {coin_emoji} **{money:,}**")
                else:
                    return await ctx.send(f"Check your wallet **{ctx.author.name}** Lmao!")
            else:
                return await ctx.send(f"**{ctx.author.name}** please enter a valid amount!")
        else:
            await ctx.send(f"**{ctx.author.name}** new to this? consider `;start` to get started")

            
    @commands.command()
    async def withdraw(self, ctx, money:str):
        search = player_search(ctx.author.id)
        stats = profile.find_one({"_id": ctx.author.id})
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")

        if search:
            if money.lower() == "all":
                money = stats['bank']
            else:
                money = convert_str_to_number(money)
            if isinstance(money, int):
                old_bank = stats['bank']
                if money <= old_bank and money > 0:
                    new_wallet = stats['wallet'] + money
                    new_bank = stats['bank'] - money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet": new_wallet}})
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"bank": new_bank}})
                    await ctx.send(f"**{ctx.author.name}** {coin_emoji} **{money:,}** withdrawn")
                else:
                    return await ctx.send("**{ctx.author.name}** duh! check your bank and try again")
            else:
                return await ctx.send(f"**{ctx.author.name}** please enter a valid amount!")
        else:
            await ctx.send(f"**{ctx.author.name}** new to this? consider `;start` to get started")
        

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def beg(self, ctx):
        search = player_search(ctx.author.id)
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")

        if search:
            chance1 = random.randint(1,11)
            if chance1 in range(2,10):
                index = leveling.find_one({"_id": ctx.author.id})
                stats = profile.find_one({"_id": ctx.author.id})
                if index is None:
                    failed_sentence = random.choice(failed_beg_choice)
                    return await ctx.send(f"{failed_sentence}")
                xp = index['xp']
                level = calculate_level(xp)
                beg_money = (level*(random.randint(1,3))+random.randint(((level+10)//10),level))*globalMultiplier
                new_wallet = stats['wallet'] + beg_money
                profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet":new_wallet}})
                await ctx.send(f"**{ctx.author.name}** you earned {coin_emoji} **{beg_money}**")
            else:
                failed_sentence = random.choice(failed_beg_choice)
                await ctx.send(f"**{ctx.author.name}** {failed_sentence}")
        else:
            command = self.bot.get_command('beg')
            command.reset_cooldown(ctx)
            welcm = new_to_this(ctx)
            await ctx.send(welcm)

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minute, seconds = divmod(int(error.retry_after), 60)
            em = discord.Embed(title=f"Try again in **{minute}m {seconds}s**.", description="", color=embed_color)
            em.set_author(name=f"{ctx.author.name}'s cooldown")
            await ctx.send(embed=em)
    

    @commands.command()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def roam(self, ctx):
        search = player_search(ctx.author.id)
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        
        if search:
            stats = profile.find_one({"_id": ctx.author.id})
            index = leveling.find_one({"_id": ctx.author.id})
            xp = index['xp']
            level = calculate_level(xp)
            roam_money = (level*random.randint(8,12)+random.randint((level//10), level))*globalMultiplier
            old_wallet = stats['wallet']
            new_wallet = old_wallet + roam_money
            profile.update_one({"_id": ctx.author.id}, {"$set": {"wallet": new_wallet}})
            roamActionChoice = random.choice(roam_choices)
            await ctx.send(f"**{ctx.author.name}** {roamActionChoice}\n**{ctx.author.name}** you get {coin_emoji} **{roam_money}**")
        else:
            command = self.bot.get_command('roam')
            command.reset_cooldown(ctx)
            welcm = new_to_this(ctx)
            await ctx.send(welcm)

    @roam.error
    async def roam_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minute, seconds = divmod(int(error.retry_after), 60)
            em = discord.Embed(title=f"Try again in **{minute}m {seconds}s**.", description="", color=embed_color)
            em.set_author(name=f"{ctx.author.name}'s cooldown")
            await ctx.send(embed=em)


    @commands.command(aliases=['cd'])
    async def cooldown(self, ctx):
        search = player_search(ctx.author.id)
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        if search:
            rewards_Cd = ""
            dy_cd = get_daily_cd(ctx.author.id)
            hr_cd = get_hourly_cd(ctx.author.id)
            rewards_Cd += f"{dy_cd}\n"
            rewards_Cd += f"{hr_cd}\n"

            earning_commands_name = ['beg', 'roam']
            earnings_cd = ""
            for x in earning_commands_name:
                command_earn_CD = self.bot.get_command(x)
                command_cd = get_earning_cd(ctx, command_earn_CD, x)
                earnings_cd += f"{command_cd}\n"

            embed = discord.Embed( color = embed_color)
            embed.add_field(name="🎁 Rewards", value=rewards_Cd, inline= False)
            embed.add_field(name=f"{coin_emoji} Earnings", value=earnings_cd, inline=False)
            embed.set_author(name=f"{ctx.author.name}'s cooldown", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            tada = new_to_this(ctx)
            return await ctx.send(tada)

    
    @commands.command(aliases=['slot'])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def slots(self, ctx, money:str):
        search = player_search(ctx.author.id)
        stats = profile.find_one({"_id": ctx.author.id})
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        if search:
            if money.lower() == 'all':
                money = stats['wallet']
            else:
                money = convert_str_to_number(money)
            
            emojis = get_emoji()
            slots_win = slots_calulate(emojis)
            chance1 = random.randint(0,3)
            chance2 = random.randint(0,2)
            index = leveling.find_one({"_id": ctx.author.id})
            xp = index['xp']
            level = calculate_level(xp)
            old_wallet = stats['wallet']
            if old_wallet == 0:
                statements = ['you can only slots 1 or more coins', "you don't have any money to slots", "check you wallet lmao"]
                return await ctx.send(f"**{ctx.author.name}** " + "{0}".format(random.choice(statements)))

            if money <= old_wallet and money > 0:
                if slots_win: # win situation
                    chance3 = random.randint(0,8)
                    if chance3 == (chance2 + chance1):
                        extra_money = level*random.randint(5,10)+money
                    else:
                        extra_money = 0
                    win_money = money+extra_money
                    new_wallet = old_wallet + win_money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet":new_wallet}})
                    embed = discord.Embed(description=f"You won {coin_emoji} **{win_money}**\n\n◖{emojis}◗", color=embed_color)
                    embed.set_author(name=f"{ctx.author.name}'s slots", icon_url=ctx.author.avatar_url)
                else:
                    new_wallet = old_wallet - money
                    profile.update_one({"_id": ctx.author.id}, {"$set":{"wallet":new_wallet}})
                    emojis = get_emoji()
                    embed = discord.Embed(description=f"You lost {coin_emoji} **{money}**\n\n◖{emojis}◗", color=embed_color)
                    embed.set_author(name=f"{ctx.author.name}'s slots", icon_url=ctx.author.avatar_url)
                
                await ctx.send(embed=embed)

            else:
                return await ctx.send(f"**{ctx.author.name}** you don't have that much coins!")
        else:
            tada = new_to_this(ctx)
            await ctx.send(tada)

    @slots.error
    async def slots_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description=f"**{ctx.author.name}** Don't spam wait atleast 1 second before typing command", color=embed_color)
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
    

    @commands.command(aliases=['cf'])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def coinflip(self, ctx, side:str, money:str):
        stats = profile.find_one({"_id": ctx.author.id})
        if stats is None:
            tada = new_to_this(ctx)
            return await ctx.send(tada)
        
        coinsides = ['heads','head', 'h', 'tails', 't', 'tail']
        if not side.lower() in coinsides:
            return await ctx.send("Choose a side `heads/tails`")
        
        if side.lower() in ['heads', 'head', 'h']:
            cf_side = 'heads'
        elif side.lower() in ['tails', 'tail', 't']:
            cf_side = 'tails'
        
        if money.lower() == "all":
            money = stats['wallet']
        else:
            money = convert_str_to_number(money)
        
        index = leveling.find_one({"_id": ctx.author.id})
        xp = index['xp']
        level = calculate_level(xp)
        
        old_wallet = stats['wallet']
        if old_wallet == 0:
            statements = ['you can only slots 1 or more coins', "you don't have any money to slots", "check you wallet lmao"]
            return await ctx.send(f"**{ctx.author.name}** " + "{0}".format(random.choice(statements)))
        
        embed = discord.Embed(description="", color=embed_color)
        embed.set_author(name=f"{ctx.author.name}'s coinflip", icon_url=ctx.author.avatar_url)
        
        if money > 0 and money <= old_wallet:
            cfSides = ['heads', 'tails']
            result = random.choice(cfSides)
            landOnSide = random.randint(1,101)
            if landOnSide == 1:
                reward = random.randint(1, money)
                reward_text = f"the {coin_emoji} landed on it's Side!"
                embed.add_field(name=f"You won {reward:,} {coin_emoji}", value=f"You chose {cf_side.capitalize()}")
                embed.set_thumbnail(url=cf_sides)
            elif cf_side.lower() == result.lower():
                reward = money
                reward_text = f"{coin_emoji} it's {result.capitalize()}"
                embed.add_field(name=f"You won {reward:,} {coin_emoji}", value=f"You chose {cf_side.capitalize()}")
                if result == 'heads':
                    embed.set_thumbnail(url=cf_head)
                else:
                    embed.set_thumbnail(url=cf_tail)
            else:
                reward = -money
                reward_text = f"it was {result.capitalize()}!"
                embed.add_field(name=f"You lost {money:,} {coin_emoji}", value=f"You chose {cf_side.capitalize()}")
                if result == 'heads':
                    embed.set_thumbnail(url=cf_head)
                else:
                    embed.set_thumbnail(url=cf_tail)
            
            new_wallet = stats['wallet'] + reward
            profile.update_one({"_id": ctx.author.id}, {"$set": {"wallet": new_wallet}})

            embed.description += reward_text
            await ctx.send(embed = embed)
    
    @coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description=f"**{ctx.author.name}** Don't spam wait atleast 1 second before typing command", color=embed_color)
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)


            






    @commands.command(aliases=['hr'])
    async def hourly(self, ctx):
        stats = profile.find_one({"_id": ctx.author.id})
        cooldown_hr = hourly_cd.find_one({"_id": ctx.author.id})
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")

        if stats:
            if cooldown_hr is None:
                index = leveling.find_one({"_id": ctx.author.id})
                xp = index['xp']
                level = calculate_level(xp)
                hourly_rewards = get_hourly_rewards(level)
                hourly_rank = get_user_rank(ctx, level)
                embed = discord.Embed(
                    title="Claimed hourly reward",
                    description=f"Hourly reward for {hourly_rank.mention}\n**+{hourly_rewards:,}** {coin_emoji}", 
                    color=embed_color)
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)

                old_wallet = stats['wallet']
                new_wallet = old_wallet + hourly_rewards
                profile.update_one({"_id": ctx.author.id}, {"$set": {"wallet": new_wallet}})

                hr_cd = datetime.datetime.utcnow() + datetime.timedelta(hours=1) # setting hourly cd
                date = datetime.datetime.utcnow()
                hourly_cd.insert_one({"_id": ctx.author.id, "hr_cd": hr_cd, "date": date})

                await ctx.send(embed=embed)

            else:
                end_cd = cooldown_hr['hr_cd']
                hr_cd = end_cd - datetime.datetime.utcnow()
                minutes, seconds = divmod(int(hr_cd.total_seconds()), 60)
                em = discord.Embed(title=f"Try again in **{minutes}m {seconds}s**.", description="", color=embed_color)
                em.set_author(name=f"{ctx.author.name}'s cooldown")
                await ctx.send(embed=em)


    @commands.command()
    async def daily(self, ctx):
        stats = profile.find_one({"_id": ctx.author.id})
        cooldown_check = daily_cd.find_one({"_id": ctx.author.id})
        imoc_check = find_imoc(ctx.author.id)
        if imoc_check is False:
            return await ctx.send(f"{ctx.author.mention} you can't do this end your previous command!")
        if stats:
            if cooldown_check is None:
                index = leveling.find_one({"_id": ctx.author.id})
                xp = index['xp']
                level = calculate_level(xp)
                member_rank = get_user_rank(ctx, level)
                daily_reward = get_daily_rewards(level)

                claim_now = datetime.datetime.utcnow()
                try:
                    last_claim = stats['last_claim']
                except:
                    last_claim = claim_now
                    profile.update_one({"_id": ctx.author.id}, {"$set": {"last_claim": claim_now}})
                try:
                    daily_streak = stats['daily_streak']
                except:
                    daily_streak = 0
                    profile.update_one({"_id": ctx.author.id}, {"$set": {"daily_streak": daily_streak}})
                total_streak = update_daily_streak(ctx, level, daily_streak, claim_now, last_claim)
                streak_bonus = get_daily_streak_bonus(ctx, level, total_streak)

                embed = discord.Embed(
                    title="Claimed daily reward",
                    description = f"Daily reward for {member_rank.mention} rank\n**+{daily_reward:,}** {coin_emoji}",
                    color= embed_color)
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_footer(text=f"Daily streak bonus {streak_bonus:,} coins")

                old_wallet = stats['wallet']
                new_wallet = old_wallet + daily_reward + streak_bonus
                profile.update_one({"_id": ctx.author.id}, {"$set": {"wallet": new_wallet}})

                dy_cd = datetime.datetime.utcnow() + datetime.timedelta(hours=24) # setting daily cd
                date = datetime.datetime.utcnow()
                daily_cd.insert_one({"_id": ctx.author.id, "daily_cd": dy_cd, "date": date})

                await ctx.send(embed=embed)
            
            else:
                end_cd = cooldown_check['daily_cd']
                dy_cd = end_cd - datetime.datetime.utcnow()
                hours, reminder = divmod(int(dy_cd.total_seconds()), 60*60)
                minutes, seconds = divmod(reminder, 60)
                em = discord.Embed(title=f"Try again in {hours}h {minutes}m {seconds}s...", description="", color=embed_color)
                em.set_author(name=f"{ctx.author.name}'s cooldown")
                await ctx.send(embed=em)
        


def setup(bot):
    bot.add_cog(Economy(bot))

