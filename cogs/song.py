import discord
from discord.ext import commands
import pymongo

class Song(commands.Cog):

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
    async def addsongs(self, ctx, *, songs):
        """Add to the K.K. songs you own
        Comma separated, ignores case/spaces/punctuation
        (ex. !addsongs AnimalCity, kk cruisin)"""
        await ctx.message.delete()
        song_list = self.__getsongs(songs)
        self.db["users"].update({"_id": ctx.message.author.id}, {"$addToSet": {"songs": {"$each": song_list}}}, True)
        await ctx.send(f"Added these songs for {ctx.message.author.mention}: {', '.join(song_list)}")

    @commands.command(pass_context = True)
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
            if "songs" not in user or song not in user["songs"]:
                users_without_song.append(user["display_name"])
            else:
                users_with_song.append(user["display_name"])

        text = f"Have :musical_note: {song}: {', '.join(users_with_song)}\n"
        text += f"Need :musical_note: {song}: {', '.join(users_without_song)}"
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
        user_song = next((s for s in user_songs if s not in partner_songs), None)
        partner_song = next((s for s in partner_songs if s not in user_songs), None)
        if user_song and partner_song:
            await ctx.send(f"{ctx.message.author.mention} needs :musical_note: {partner_song} and {member.mention} needs :musical_note: {user_song}, zzrrbbitt!")
        else:
            await ctx.send("No valid trade can be made, zzrrbbitt!")