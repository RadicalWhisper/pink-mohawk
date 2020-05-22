"""
Created on 16 May 2020
@author: John Thomas
"""
from os import environ
import discord
from discord.ext import commands
import random
import math
import lookup
import dice
import re
import json
from translations import string_builder, get_channel_language, load_strings, set_channel_language
from enum import Enum
from data import DB

class Languages(Enum):
    EN = "English"
    DE = "Deutsch"

TOKEN = environ['DISCORD_TOKEN']
COMMAND_PREFIX = environ['DISCORD_COMMAND_PREFIX']
load_strings()

bot = commands.Bot(command_prefix=COMMAND_PREFIX)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Shadowrun | " + COMMAND_PREFIX + "help"))
            

@bot.command(aliases=["lang"])
async def language(ctx, language):
    languages = {"en":"English", "de":"Deutsch"}
    if language in languages:
        set_channel_language(ctx.message.channel.id, language)
        await ctx.send(string_builder("set_language", language) % (languages[language]))
    else:
        await ctx.send("\"" + language + "\"" + " is not a supported language code.")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(aliases=['s'])
async def search(ctx, entry_type=None, search=None):
    if entry_type is None:
        await ctx.send("Matrix Search usage: `>search [type] [entry]`\nIf the entry is multiple words, they must be wrapped in double quotes (\"\").\nAvailable types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() not in lookup.ENTRY_TYPES:
        await ctx.send("Matrix Search failed: \"" + entry_type + "\" is not an avaiable type. Available types: weapon, armor, matrix, gear, augmentation, streetpedia.")
        return

    if entry_type.lower() == "weapon":
        if search is None:
            await ctx.send("Command requires `[entry]`. Please try your search again.")

        await ctx.send("Performing Matrix search for \"" + search + "\"...")    
        weapon = lookup.lookup_weapon(search)
   
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
    
    if entry_type.lower() in lookup.ENTRY_TYPES:
        await ctx.send("There are currently no armor entries for that type in the database.")

@bot.command(aliases=["r","würfeln"])
async def roll(ctx, command, threshold=None):
    dice_pool = int(re.search('[0-9]+', command).group())
    if dice_pool > 100:
        results = string_builder("too_many_dice", get_channel_language(ctx.message.channel.id))
        await ctx.send(results)
        return
    
    results = (string_builder("rolling", get_channel_language(ctx.message.channel.id)) % (dice_pool, "(" + str(threshold) + ")" if threshold is not None else "", str(ctx.message.author.mention)))

    roll_results = dice.roll_pool(command)
    hits = roll_results[2]
    pool = roll_results[0]
    wild = roll_results[1]
    glitched = roll_results[3]
    results += ("\n**" + str(hits) + "** hits " + str(pool))
    if wild != 0: results += "[" + str(wild) + "]"

    if threshold is not None:
        if hits >= int(threshold):
            results += (string_builder("success", get_channel_language(ctx.message.channel.id)))
        else:
            results += (string_builder("failure", get_channel_language(ctx.message.channel.id)))    

    if glitched and hits == 0:
        results += ("\n:bangbang:**CRITICAL GLITCH**:bangbang:")
    elif glitched:
        results += ("\n:bangbang:**GLITCH**:bangbang:")

     

    await ctx.send(results)
    await ctx.message.delete()
        


@bot.command()
async def buyhits(ctx, dice: int):
    hits = math.floor(dice / 4)
    await ctx.send("%s bought %i hits from %i:game_die:." % (ctx.message.author.mention, hits, dice))
    await ctx.message.delete()


@bot.command()
async def legal(ctx):
    await ctx.send("The Topps Company, Inc. has sole ownership of the names, logo, artwork, marks, photographs, sounds, audio, video and/or any proprietary material used in connection with the game Shadowrun. The Topps Company, Inc. has granted permission to Pink Mohawk to use such names, logos, artwork, marks and/or any proprietary materials for promotional and informational purposes on its website but does not endorse, and is not affiliated with Pink Mohawk in any official capacity whatsoever.")
    await ctx.message.delete()


@bot.command()
async def about(ctx):
    embed = discord.Embed(title="Pink Mohawk", description="A Discord bot for playing Shadowrun Sixth World", color=0xff69b4)
    embed.set_thumbnail(url="https://i.imgur.com/Y1ZrwN7.png")
    embed.add_field(name="Developer", value="John 'JT' Thomas", inline=False)
    embed.add_field(name="Documentation", value="https://docs.mohawk.pink/", inline=False)
    embed.add_field(name="GitHub", value="https://github.com/pink-mohawk/pink-mohawk-bot", inline=False)
    embed.add_field(name="Site", value="https://mohawk.pink", inline=False)
    embed.set_footer(text="2020 © John Thomas")
    await ctx.send(embed=embed)


@bot.command(aliases=["contributors"])
async def credits(ctx):
    with open("data/contributors.json", "r") as json_file:
        contributors = json.load(json_file)
        contributors.sort()
        await ctx.send(":heart:**CONTRIBUTORS**:heart:\n" + "\n".join(contributors))
        await ctx.message.delete()

        
bot.run(TOKEN)
