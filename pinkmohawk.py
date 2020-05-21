"""
Created on 16 May 2020
@author: John Thomas
"""
from os import environ
import discord
from discord.ext import commands
import random
import math
from enum import Enum
from lookup import *
from dice import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

cred = credentials.Certificate('firebase-service-account.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

TOKEN = environ['DISCORD_TOKEN']
COMMAND_PREFIX = environ['DISCORD_COMMAND_PREFIX']

class Language(Enum):
    ENGLISH = 1
    GERMAN = 2


bot = commands.Bot(command_prefix=COMMAND_PREFIX)
savedPool = []

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Shadowrun 6e"))
            

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases=['de'])
async def en(ctx):
    if ctx.invoked_with == "de":

        await ctx.send("de")
    else:
        await ctx.send("en")

@bot.command(aliases=['s'])
async def search(ctx, entry_type=None, search=None):
    if entry_type is None:
        await ctx.send("Matrix Search usage: `>search [type] [entry]`\nIf the entry is multiple words, they must be wrapped in double quotes (\"\").\nAvailable types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() not in ENTRY_TYPES:
        await ctx.send("Matrix Search failed: \"" + entry_type + "\" is not an avaiable type. Available types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() == "weapon":
        if search is None:
            await ctx.send("Command requires `[entry]`. Please try your search again.")

        await ctx.send("Performing Matrix search for \"" + search + "\"...")    
        weapon = lookup_weapon(search)
   
        if weapon is None:
            await ctx.send("Couldn't find a Matrix entry for \"" + search + "\". Try again.")
            await ctx.message.delete()
            return

        attackRatings = weapon["attack_ratings"]["close"] + "/" + weapon["attack_ratings"]["near"] + "/" + weapon["attack_ratings"]["medium"] + "/" + weapon["attack_ratings"]["far"] + "/" + weapon["attack_ratings"]["extreme"]

        embed = discord.Embed(title=weapon["name"], description=weapon["description"], color=0x00ff00)
        embed.add_field(name="DV", value=weapon["damage_value"], inline=False)
        embed.add_field(name="Attack Ratings", value=attackRatings, inline=False)
        embed.add_field(name="Availability", value=weapon["availability"], inline=False)
        embed.add_field(name="Cost", value=weapon["cost"] + u'\u00A5', inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()
    
    if entry_type.lower() in ENTRY_TYPES:
        await ctx.send("There are currently no armor entries for that type in the database.")

@bot.command(aliases=['r','würfeln'])
async def roll(ctx, command, threshold=None):
    language = Language.ENGLISH
    results = ""
    if ctx.invoked_with == "würfeln":
        language = Language.GERMAN

    dice = int(re.search('[0-9]+', command).group())
    if dice > 100:
        if language == Language.ENGLISH:
            results = db.collection(u'strings').document(u'too_many_dice').get().to_dict()["en"]
        elif language == Language.GERMAN:
            results = db.collection(u'strings').document(u'too_many_dice').get().to_dict()["de"]
        await ctx.send(results)
        return

    results = ("Rolling " + str(dice) + ":game_die:")
    if threshold is not None:
        threshold = int(threshold)
        results += "(" + str(threshold) + ")"
    results += " for " + str(ctx.message.author.mention)

    roll_results = roll_pool(command)
    hits = roll_results[2]
    pool = roll_results[0]
    wild = roll_results[1]
    glitched = roll_results[3]
    results += ("\n**" + str(hits) + "** hits " + str(pool))
    if wild != 0: results += "[" + str(wild) + "]"

    if glitched and hits == 0:
        results += ("\n:bangbang:**CRITICAL GLITCH**:bangbang:")
    elif glitched:
        results += ("\n:bangbang:**GLITCH**:bangbang:")

    if threshold is not None:
        if hits >= threshold:
            results += ("\n**SUCCESS**")
        else:
            results += ("\n**FAILURE**")     

    await ctx.send(results)
    await ctx.message.delete()
        
@bot.command(aliases=['rr'])
async def reroll(ctx, rollval : int):
    try:
        if len(savedPool) > 0:
            for r in savedPool:
                if savedPool[r] == rollval:
                    newval = random.randint(1, 6)
                    print("New value: " + str(newval))
                    savedPool[r] = newval
                    savedPool.sort()
                    await ctx.send("%s rerolled a %i and got a %i instead. The new dice pool is below:" % (ctx.message.author.mention, rollval, newval))
                    resultString = ("Hits: **" + str(get_hits(savedPool)) + "** " + str(savedPool))
                    await ctx.send(resultString)
                    return
                else:
                    await ctx.send("There are no %is in the active dice pool. Try again." % (rollval))
        else:
            await ctx.send("There is nothing to reroll. Try rolling first.")

    except Exception as e:
        print("Error: " + str(e))
        await ctx.send("Error: " + str(e))
        return


@bot.command()
async def buyhits(ctx, dice: int):
    hits = math.floor(dice / 4)
    await ctx.send("%s bought %i hits from %i:game_die:." % (ctx.message.author.mention, hits, dice))
    await ctx.message.delete()

@bot.command()
async def adp(ctx):
    # Prints the current active dice pool with hits and glitches
    await ctx.send("The current active dice pool is:")
    await ctx.send("Hits: **" + str(get_hits(savedPool)) + "** " + str(savedPool))
    await ctx.message.delete()


@bot.command()
async def legal(ctx):
    await ctx.send("The Topps Company, Inc. has sole ownership of the names, logo, artwork, marks, photographs, sounds, audio, video and/or any proprietary material used in connection with the game Shadowrun. The Topps Company, Inc. has granted permission to Pink Mohawk to use such names, logos, artwork, marks and/or any proprietary materials for promotional and informational purposes on its website but does not endorse, and is not affiliated with Pink Mohawk in any official capacity whatsoever.")
    await ctx.message.delete()


@bot.command()
async def about(ctx):
    embed = discord.Embed(title="Pink Mohwak", description="A Discord bot for playing Shadowrun 6e online", color=0xff69b4)
    embed.set_thumbnail(url=ctx.message.guild.icon_url)
    embed.add_field(name="Developer", value="John 'JT' Thomas (Whisper)")
    embed.add_field(name="GitHub", value="https://github.com/pink-mohawk/pink-mohawk-bot")
    embed.add_field(name="Site", value="https://mohawk.pink")
    embed.set_footer(text="2020 © John Thomas")
    await ctx.send(embed=embed)
    

bot.run(TOKEN)
