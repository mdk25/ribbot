import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
import os
import pymongo

from cogs import queue, song, user, villager

##### Configuration #####
prefix = "!"
approved_roles = ["Admin", "admin"]
#########################

bot = commands.Bot(command_prefix = prefix, case_insensitive = True)
token = os.environ.get("DISCORD_TOKEN")
client = pymongo.MongoClient(os.environ.get("MONGODB_URI"))
db = client[os.environ.get("MONGODB_DATABASE")]

def is_approved(ctx):
    if any(role.name in approved_roles for role in ctx.message.author.roles):
        return True
    return False

def approved():
    def predicate(ctx):
        return is_approved(ctx)
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        if ctx.invoked_with[0].isalpha():
            await ctx.send(f"{ctx.invoked_with} isn't a command, zzrrbbitt! Check the list with: !help")
        return
    if isinstance(error, MissingRequiredArgument):
        await ctx.send(f"{ctx.invoked_with} is missing arguments, zzrrbbitt! Check how to use it with: !help {ctx.invoked_with}")
        return
    raise error

bot.add_cog(queue.Queue(bot, is_approved))
bot.add_cog(song.Song(bot, db))
bot.add_cog(user.User(bot, db))
bot.add_cog(villager.Villager(bot, db))
bot.run(token)