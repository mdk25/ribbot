from cogs import queue
from cogs import song
from cogs import user

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import os
import pymongo

##### Configuration #####
prefix = "!"
approved_roles = ["Admin", "admin"]
#########################

bot = commands.Bot(command_prefix = prefix, case_insensitive = True)
token = os.environ.get("DISCORD_TOKEN")
client = pymongo.MongoClient(os.environ.get("MONGODB_URI") + "?retryWrites=false")
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
        return
    raise error

bot.add_cog(queue.Queue(bot, is_approved))
bot.add_cog(song.Song(bot, db))
bot.add_cog(user.User(bot, db))
bot.run(token)