from pymongo import MongoClient
import discord

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