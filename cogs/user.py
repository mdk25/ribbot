from datetime import datetime
import discord
from discord.ext import commands
import pymongo
import pytz

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
    async def profile(self, ctx, member: discord.Member = None):
        """View someone's profile
        (ex. !profile @Ribbot)"""
        await ctx.message.delete()
        if not member:
            member = ctx.message.author
        user = self.db["users"].find_one({"_id": member.id})
        if not user:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        text = f"Here's what I know about {member.mention}, zzrrbbitt!\n"
        if "name" in user:
            text += f"**Name:** {user['name']}\n"
        if "island" in user:
            text += f"**Island:** {user['island']}\n"
        if "friend_code" in user:
            text += f"**Friend Code:** {user['friend_code']}\n"
        if "timezone" in user:
            tz = pytz.timezone(user["timezone"])
            text += f"**Time Zone:** {user['timezone']} ({datetime.now(tz).strftime('%b %d %I:%M %p')})\n"
        if "stalks" in user:
            text += f"**Stalks.io Username:** {user['stalks']}\n"
        if "nookazon" in user:
            text += f"**Nookazon Profile:** <{user['nookazon']}>\n"
        if "songs" in user:
            text += f"**Songs:** {len(user['songs'])}\n"
        if "notes" in user:
            text += f"**Notes:** {user['notes']}\n"
        await ctx.send(text)

    @commands.command(pass_context = True)
    async def setname(self, ctx, name):
        """Set your character name
        (ex. !setname Ribbot)"""
        await ctx.message.delete()
        name = name.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"name": name, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated name for {ctx.message.author.mention} to: **{name}**")

    @commands.command(pass_context = True)
    async def setisland(self, ctx, *, island):
        """Set your island name
        (ex. !setisland Iron Island)"""
        await ctx.message.delete()
        island = island.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"island": island, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated island for {ctx.message.author.mention} to: **{island}**")

    @commands.command(pass_context = True)
    async def setfriendcode(self, ctx, friend_code):
        """Set your friend code
        (ex. !setfriendcode SW-XXXX-XXXX-XXXX)"""
        await ctx.message.delete()
        friend_code = friend_code.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"friend_code": friend_code, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated friend code for {ctx.message.author.mention} to: **{friend_code}**")

    @commands.command(pass_context = True)
    async def settimezone(self, ctx, timezone):
        """Set your time zone
        Use a time zone from the 'TZ database name' column in this table: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        (ex. !settimezone America/New_York)"""
        await ctx.message.delete()
        if timezone not in pytz.all_timezones:
            await ctx.send("That isn't a valid time zone, zzrrbbitt!")
            return
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"timezone": timezone, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated time zone for {ctx.message.author.mention} to: **{timezone}**")

    @commands.command(pass_context = True)
    async def setstalks(self, ctx, stalks_username):
        """Set your Stalks.io username
        (ex. !setstalks ribbot)"""
        await ctx.message.delete()
        stalks_username = stalks_username.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"stalks": stalks_username, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated Stalks.io username for {ctx.message.author.mention} to: **{stalks_username}**")

    @commands.command(pass_context = True)
    async def setnookazon(self, ctx, nookazon_profile):
        """Set your Nookazon profile
        (ex. !setnookazon https://nookazon.com/profile/1)"""
        await ctx.message.delete()
        nookazon_profile = nookazon_profile.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"nookazon": nookazon_profile, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated Nookazon profile for {ctx.message.author.mention} to: **{nookazon_profile}**")

    @commands.command(pass_context = True)
    async def setnotes(self, ctx, *, notes):
        """Set notes on your profile
        (ex. !setnotes I might be a robot, but I'm still a frog, zzrrbbitt!)"""
        await ctx.message.delete()
        notes = notes.replace("@", "@\N{zero width space}")
        self.db["users"].update({"_id": ctx.message.author.id}, {"$set": {"notes": notes, "display_name": ctx.message.author.display_name}}, True)
        await ctx.send(f"Updated notes for {ctx.message.author.mention} to: **{notes}**")
