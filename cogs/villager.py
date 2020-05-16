import discord
from discord.ext import commands
import pymongo

class Villager(commands.Cog):

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def __getvillager(self, villager):
        id = "".join(ch for ch in villager.lower() if ch.isalnum())
        saved_villager = self.db["villagers"].find_one({"_id": id})
        if saved_villager:
            return saved_villager
        return None

    @commands.command(pass_context = True)
    async def tier(self, ctx, *, villager):
        """View the tier of a villager
        Ignores case/spaces/punctuation
        (ex. !tier Ribbot)"""
        await ctx.message.delete()
        v = self.__getvillager(villager)
        if not v:
            await ctx.send("I don't know that villager, zzrrbbitt!")
            return

        tier = v["tier"]
        if v["_id"] == "ribbot":
            tier = "S"

        text = f"**{v['name']}** is in **Tier {tier}**. "
        if tier == "S":
            text += "Clearly the best, zzrrbbitt!"
        elif tier == 1:
            text += "That's a keeper, zzrrbbitt!"
        elif tier == 2:
            text += "Almost good enough, zzrrbbitt!"
        elif tier == 3:
            text += "There are better, zzrrbbitt!"
        elif tier == 4:
            text += "Very mediocre, zzrrbbitt!"
        elif tier == 5:
            text += "That's a bad villager, zzrrbbitt!"
        elif tier == 6:
            text += "Dispose of that trash, zzrrbbitt!"

        await ctx.send(text)