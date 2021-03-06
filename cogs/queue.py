import discord
from discord.ext import commands
import typing

class QueueDetails:

    def __init__(self, owner, note, message = None):
        self.queue = []
        self.owner = owner
        self.note = note
        self.message = message

class Queue(commands.Cog):

    def __init__(self, bot, is_approved):
        self.bot = bot
        self.is_approved = is_approved
        self.queues = {}

    async def __find_queue(self, ctx, owner):
        if owner:
            if owner.id in self.queues:
                return self.queues[owner.id]
            else:
                await ctx.send(f"Queue for {owner.mention} is not open, zzrrbbitt!")
                return None
        elif len(self.queues) == 1:
            return list(self.queues.values())[0]
        elif len(self.queues) == 0:
            await ctx.send("No queues are open right now, zzrrbbitt!")
            return None
        else:
            await ctx.send(f"You need to specify the queue owner, {ctx.message.author.mention}, zzrrbbitt!")
            return None

    async def __show_queue(self, ctx, details):
        text = f"Queue for {details.owner.mention} is open, zzrrbbitt!\n"
        text += "Use **!join** to add yourself and **!leave** when you're done or to exit the queue.\n\n"
        if details.note:
            text += f"{details.note}\n\n"

        qtext = ""
        for position, user_id in enumerate(details.queue):
            user = ctx.guild.get_member(user_id)
            qtext += f"**#{position + 1}: "
            if position == 0:
                qtext += f"{user.mention}** - you're up!\n"
            elif position == 1:
                qtext += f"{user.display_name}** - up next!\n"
            else:
                qtext += f"{user.display_name}**\n"
        if qtext == "":
            qtext = "Queue is empty"
        text += qtext

        if details.message:
            await details.message.delete()
        details.message = await ctx.send(text)

    @commands.command(pass_context = True)
    async def open(self, ctx, owner: typing.Optional[discord.Member] = None, *, note = None):
        """Create a new queue
        (ex. !open This is an optional note)
        Admin only: Create a new queue for someone else
        (ex. !open @Ribbot This is an optional note)"""
        await ctx.message.delete()
        if not owner:
            owner = ctx.message.author
        elif not self.is_approved(ctx):
            note = f"{owner.mention}{'' if not note else ' ' + note}"
            owner = ctx.message.author

        if owner.id in self.queues:
            await ctx.send(f"Queue for {owner.mention} was already open, zzrrbbitt!")
        else:
            details = QueueDetails(owner, note)
            await self.__show_queue(ctx, details)
            self.queues[owner.id] = details

    @commands.command(pass_context = True)
    async def note(self, ctx, owner: typing.Optional[discord.Member] = None, *, note):
        """Set the note on your queue
        (ex. !note This is a note)
        Admin only: Set the note on someone else's queue
        (ex. !note @Ribbot This is a note)"""
        await ctx.message.delete()
        if not owner or not self.is_approved(ctx):
            owner = ctx.message.author

        if owner.id in self.queues:
            details = self.queues[owner.id]
            details.note = note
            await self.__show_queue(ctx, details)
        else:
            await ctx.send(f"Queue for {owner.mention} is not open, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def join(self, ctx, owner: discord.Member = None, member: discord.Member = None):
        """Join a queue
        (ex. !join)
        Join a particular queue
        (ex. !join @Ribbot)
        Admin/Queue Owner only: Make someone else join a particular queue
        (ex. !join @Ribbot @Zira)"""
        await ctx.message.delete()
        details = await self.__find_queue(ctx, owner)
        if not details:
            return

        if not member or (ctx.message.author.id != details.owner.id and not self.is_approved(ctx)):
            member = ctx.message.author
        if member.id not in details.queue:
            details.queue.append(member.id)

        await self.__show_queue(ctx, details)

    @commands.command(pass_context = True)
    async def leave(self, ctx, owner: discord.Member = None, member: discord.Member = None):
        """Leave a queue
        (ex. !leave)
        Leave a particular queue
        (ex. !leave @Ribbot)
        Admin/Queue Owner only: Make someone else leave a particular queue
        (ex. !leave @Ribbot @Zira)"""
        await ctx.message.delete()
        details = await self.__find_queue(ctx, owner)
        if not details:
            return

        if not member or (ctx.message.author.id != details.owner.id and not self.is_approved(ctx)):
            member = ctx.message.author
        if member.id in details.queue:
            details.queue.remove(member.id)

        await self.__show_queue(ctx, details)

    @commands.command(pass_context = True)
    async def skip(self, ctx, owner: discord.Member = None):
        """Skip the first person in your queue
        (ex. !skip)
        Admin only: Skip the first person in someone else's queue
        (ex. !skip @Ribbot)"""
        await ctx.message.delete()
        if not owner or not self.is_approved(ctx):
            owner = ctx.message.author

        if owner.id in self.queues:
            details = self.queues[owner.id]
            if len(details.queue) < 2:
                return
            skipped = details.queue[0]
            details.queue[0] = details.queue[1]
            details.queue[1] = skipped
            await self.__show_queue(ctx, details)
        else:
            await ctx.send(f"Queue for {owner.mention} is not open, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def clear(self, ctx, owner: discord.Member = None):
        """Clear your queue
        (ex. !clear)
        Admin only: Clear someone else's queue
        (ex. !clear @Ribbot)"""
        await ctx.message.delete()
        if not owner or not self.is_approved(ctx):
            owner = ctx.message.author

        if owner.id in self.queues:
            details = self.queues[owner.id]
            details.queue = []
            await self.__show_queue(ctx, details)
        else:
            await ctx.send(f"Queue for {owner.mention} is not open, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def close(self, ctx, owner: discord.Member = None):
        """Close your queue
        (ex. !close)
        Admin only: Close someone else's queue
        (ex. !close @Ribbot)"""
        await ctx.message.delete()
        if not owner or not self.is_approved(ctx):
            owner = ctx.message.author

        if owner.id in self.queues:
            details = self.queues[owner.id]
            details.queue = []
            await details.message.delete()
            del self.queues[owner.id]
            await ctx.send(f"Queue for {owner.mention} has been closed, zzrrbbitt!")
        else:
            await ctx.send(f"Queue for {owner.mention} was already closed, zzrrbbitt!")

    @commands.command(pass_context = True)
    async def listing(self, ctx):
        """List all open queues
        (ex. !listing)"""
        await ctx.message.delete()
        if len(self.queues) == 0:
            await ctx.send("No queues are open right now, zzrrbbitt!")
            return
        
        text = "There are open queues for:\n"
        for details in list(self.queues.values()):
            text += f"{details.owner.mention}\n"
        await ctx.send(text)
