"""
Created on 25 May 2020
@author: John Thomas
"""
import discord
from discord.ext import commands
from translations import string_builder, get_channel_language, load_strings, set_channel_language
from data import DB

class CombatTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["c"], invoke_without_command=True)
    async def combat(self, ctx):
        """Commands to help track combat."""
        await ctx.send(f"Incorrect usage. Use `{ctx.prefix}help combat` for help.")


    @combat.command()
    async def start(self, ctx):
        if get_combat_state(ctx.message.channel.id):
            await ctx.send("Channel is already in combat!")
        else:
            set_combat_state(ctx.message.channel.id, True)
            await ctx.send("Combat started. Type `%scombat join` to join." % (ctx.prefix))

    @combat.command()
    async def end(self, ctx):
        if get_combat_state(ctx.message.channel.id):
            set_combat_state(ctx.message.channel.id, False)
            await ctx.send("Combat ended.")
        else:
            await ctx.send("Channel is not in combat.")

    @combat.command()
    async def add(self, ctx, name="Lone Star Patrolman", init="6+1", *args):
        """Adds an NPC to combat. If no arguments are passed, the
        statblock for a Lone Star Patrolman is used (SR6,p206).
        """
        if get_combat_state(ctx.message.channel.id):
            add_combatant(ctx.message.channel.id, name, 6)
            results = "```\nCombat Tracker | Round: 0 | Initializing combat...\n6: %s\n```" % (name)
            await ctx.send(results)

def add_combatant(id, name, init):
    channel_ref = DB.collection("channels").document(str(id))
    channel_ref.set(
        {
            "combat" : {
                "combatants" : {
                    "name" : name,
                    "iscore" : init
                }
            }
        }, merge=True
    )                

def get_combat_state(id):
    channel_ref = DB.collection("channels").document(str(id))
    channel = channel_ref.get()
    if channel.exists:
        if channel.to_dict()["combat"]["in_combat"] is not None:
            return channel.to_dict()["combat"]["in_combat"]
        else:
            channel_ref.set(
                {
                    "combat" : {
                        "in_combat" : False
                    }
                }, merge=True
            )
            return False


def set_combat_state(id, combat):
    channel_ref = DB.collection("channels").document(str(id))
    channel_ref.set(
        {
            "combat" : {
                "in_combat" : combat
            }
        }, merge=True
    )

def setup(bot):
    bot.add_cog(CombatTracker(bot))