import discord
from discord.ext import commands
import pymongo

class Song(commands.Cog):

    untradeable = {"Animal City", "Drivin'", "Farewell", "K.K. Birthday"}

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def __getsong(self, song):
        id = "".join(ch for ch in song.lower() if ch.isalnum())
        saved_song = self.db["songs"].find_one({"_id": id})
        if saved_song and "name" in saved_song:
            return saved_song["name"]
        return None

    def __getsongs(self, songs):
        song_list = []
        for song in songs.split(","):
            song_name = self.__getsong(song)
            if song_name:
                song_list.append(song_name)
        return song_list

    @commands.command(pass_context = True)
    async def songlist(self, ctx, member: discord.Member = None):
        """View your song list
        (ex. !songlist)
        View someone's song list
        (ex. !songlist @Ribbot)"""
        await ctx.message.delete()
        if not member:
            member = ctx.message.author
        user = self.db["users"].find_one({"_id": member.id})
        if not user:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        if "songs" in user and user["songs"]:
            user["songs"].sort()
            await ctx.send(f"Song list for {member.mention}: {', '.join(user['songs'])}")
        else:
            await ctx.send(f"{member.mention} doesn't have any songs yet, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def missingsongs(self, ctx, member: discord.Member = None):
        """View songs missing from your list
        (ex. !missingsongs)
        View songs missing from someone's list
        (ex. !missingsongs @Ribbot)"""
        await ctx.message.delete()
        if not member:
            member = ctx.message.author
        user = self.db["users"].find_one({"_id": member.id})
        if not user:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        if "songs" in user and user["songs"]:
            user_songs = set(user["songs"])
            all_songs = self.db["songs"].find()
            missing = (s["name"] for s in all_songs if s["name"] not in user_songs)
            if missing:
                await ctx.send(f"Missing songs for {member.mention}: {', '.join(missing)}")
            else:
                await ctx.send(f"{member.mention} has every song, zzrrbbitt!")
        else:
            await ctx.send(f"{member.mention} doesn't have any songs yet, zzrrbbitt!")

    @commands.command(pass_context = True, aliases = ["addsong"])
    async def addsongs(self, ctx, *, songs):
        """Add to the K.K. songs you own
        Comma separated, ignores case/spaces/punctuation
        (ex. !addsongs AnimalCity, kk cruisin)"""
        await ctx.message.delete()
        song_list = self.__getsongs(songs)
        self.db["users"].update({"_id": ctx.message.author.id}, {"$addToSet": {"songs": {"$each": song_list}}}, True)
        await ctx.send(f"Added these songs for {ctx.message.author.mention}: {', '.join(song_list)}")

    @commands.command(pass_context = True, aliases = ["removesong"])
    async def removesongs(self, ctx, *, songs):
        """Remove from the K.K. songs you own
        Comma separated, ignores case/spaces/punctuation
        (ex. !removesongs AnimalCity, kk cruisin)"""
        await ctx.message.delete()
        song_list = self.__getsongs(songs)
        self.db["users"].update({"_id": ctx.message.author.id}, {"$pullAll": {"songs": song_list}}, True)
        await ctx.send(f"Removed these songs for {ctx.message.author.mention}: {', '.join(song_list)}")

    @commands.command(pass_context = True)
    async def song(self, ctx, *, song):
        """See who has or is missing a K.K. song
        Ignores case/spaces/punctuation
        (ex. !song kk cruisin)"""
        await ctx.message.delete()
        song = self.__getsong(song)
        if not song:
            await ctx.send("I don't know that song, zzrrbbitt!")
            return

        users_with_song = []
        users_without_song = []
        users = self.db["users"].find()
        for user in users:
            if "songs" not in user or not user["songs"]:
                continue
            if song in user["songs"]:
                users_with_song.append(user["display_name"])
            else:
                users_without_song.append(user["display_name"])

        text = f"Have :musical_note: **{song}**: {', '.join(users_with_song)}\n"
        text += f"Need :musical_note: **{song}**: {', '.join(users_without_song)}"
        await ctx.send(text)

    @commands.command(pass_context = True)
    async def songtrade(self, ctx, member: discord.Member):
        """Set up a song trade with someone else
        (ex. !songtrade @Ribbot)"""
        await ctx.message.delete()
        user = self.db["users"].find_one({"_id": ctx.message.author.id})
        partner = self.db["users"].find_one({"_id": member.id})
        if not user or not partner:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        if "songs" not in user or "songs" not in partner:
            await ctx.send("No songs found to make a trade, zzrrbbitt!")
            return

        user_songs = set(user["songs"])
        partner_songs = set(partner["songs"])
        user_song = next((s for s in user_songs if s not in partner_songs and s not in Song.untradeable), None)
        partner_song = next((s for s in partner_songs if s not in user_songs and s not in Song.untradeable), None)
        if user_song and partner_song:
            await ctx.send(f"{ctx.message.author.mention} needs :musical_note: **{partner_song}** and {member.mention} needs :musical_note: **{user_song}**, zzrrbbitt!")
        else:
            await ctx.send("No valid trade can be made, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def songgift(self, ctx, member: discord.Member):
        """Gift a song to someone else
        (ex. !songgift @Ribbot)"""
        await ctx.message.delete()
        user = self.db["users"].find_one({"_id": ctx.message.author.id})
        partner = self.db["users"].find_one({"_id": member.id})
        if not user or not partner:
            await ctx.send("I don't know who that is, zzrrbbitt!")
            return
        if "songs" not in user:
            await ctx.send("No songs found to gift, zzrrbbitt!")
            return
        if "songs" not in partner:
            await ctx.send("I don't know what songs they have, zzrrbbitt!")
            return

        user_songs = set(user["songs"])
        partner_songs = set(partner["songs"])
        user_song = next((s for s in user_songs if s not in partner_songs and s not in Song.untradeable), None)
        if user_song:
            await ctx.send(f"{member.mention} needs :musical_note: **{user_song}**, zzrrbbitt!")
        else:
            await ctx.send("No songs found to gift, zzrrbbitt!")
