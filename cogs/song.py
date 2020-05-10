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
        """: Add the K.K. songs you own"""
        await ctx.message.delete()
        song_list = self.__getsongs(songs)
        self.db["users"].update({"_id": ctx.message.author.id}, {"$addToSet": {"songs": {"$each": song_list}}}, True)
        await ctx.send(f"Added these songs for {ctx.message.author.mention}: {', '.join(song_list)}")

    @commands.command(pass_context = True)
    async def removesongs(self, ctx, *, songs):
        """: Remove from the K.K. songs you own"""
        await ctx.message.delete()
        song_list = self.__getsongs(songs)
        self.db["users"].update({"_id": ctx.message.author.id}, {"$pullAll": {"songs": song_list}}, True)
        await ctx.send(f"Removed these songs for {ctx.message.author.mention}: {', '.join(song_list)}")

    @commands.command(pass_context = True)
    async def song(self, ctx, *, song):
        """: See who has or doesn't have a K.K. song"""
        await ctx.message.delete()
        song = self.__getsong(song)
        if not song:
            await ctx.send("I don't know that song, zzrrbbitt!")
            return

        users_with_song = []
        users_without_song = []
        users = self.db["users"].find()
        for user in users:
            if not "songs" in user or not song in user["songs"]:
                users_without_song.append(user["display_name"])
            else:
                users_with_song.append(user["display_name"])

        text = f"Have {song}: {', '.join(users_with_song)}\n"
        text += f"Need {song}: {', '.join(users_without_song)}"
        await ctx.send(text)
