import discord
from discord.ext import commands
import pymongo

class User(commands.Cog):

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command(pass_context = True)
    async def me(self, ctx):
        """View your profile
        (ex. !me)"""
        await self.profile(ctx, ctx.message.author)

    @commands.command(pass_context = True)
    async def profile(self, ctx, member: discord.Member):
        """View someone's profile
        (ex. !profile @Ribbot)"""
        await ctx.message.delete()
        user = self.db["users"].find_one({"_id": member.id})
        if not user:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        text = f"Here's what I know about {member.mention}, zzrrbbitt!\n"
        if "name" in user:
            text += f"Name: {user['name']}\n"
        if "island" in user:
            text += f"Island: {user['island']}\n"
        if "friend_code" in user:
            text += f"Friend Code: {user['friend_code']}\n"
        if "songs" in user:
            text += f"Song List: {', '.join(user['songs'])}\n"
        await ctx.send(text)

    @commands.command(pass_context = True)
    async def setname(self, ctx, name):
        """Set your character name
        (ex. !setname Ribbot)"""
        await ctx.message.delete()
        name = name.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"name": name, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated name for {ctx.message.author.mention} to: {name}")

    @commands.command(pass_context = True)
    async def setisland(self, ctx, *, island):
        """Set your island name
        (ex. !setisland Iron Island)"""
        await ctx.message.delete()
        island = island.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"island": island, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated island for {ctx.message.author.mention} to: {island}")

    @commands.command(pass_context = True)
    async def setfriendcode(self, ctx, friend_code):
        """Set your friend code
        (ex. !setfriendcode SW-XXXX-XXXX-XXXX)"""
        await ctx.message.delete()
        friend_code = friend_code.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"friend_code": friend_code, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated friend code for {ctx.message.author.mention} to: {friend_code}")
