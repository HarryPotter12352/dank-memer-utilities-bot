import discord
from discord.ext import commands, tasks
from itertools import cycle
from datetime import datetime
import asyncio 
import random

CHANNEL_ID = ""
client = commands.Bot(command_prefix="ed!", intents = discord.Intents.all())

status_list = cycle(
    ["ed!help", "general", "Exile Dankers", "Minecraft"]
)

@client.event 
async def on_ready():
    print(f"{client.user} is now ready!")
    await client.wait_until_ready()
    await change_status.start()


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(name=next(status_list)))


def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1

    try:
        val = int(time[:-1])
    except:
        return -2


    return val * time_dict[unit]


@client.command()
@commands.has_role("Giveaway Manager")
async def giveaway(ctx, channel : discord.TextChannel, time : str, *, prize : str):
    converted_time = convert(time)

    if converted_time == -1 or -2:
        await ctx.send(f"Please provide valid time arguments!")

    else:
        ending_time = datetime.utcnow() + converted_time
        embed = discord.Embed(titlt=f"New giveaway!", description=f"{prize}", colour = discord.Colour.random(), timestamp=datetime.now())
        embed.add_field(name='Hosted by', value = f"{ctx.author}", inline = False)
        embed.add_field(name="Ends at", value = ending_time, inline = False)
        msg = await channel.send(embed=embed)

        await asyncio.sleep(converted_time)

        reactions = msg.reactions.pop(client.user)
        users = reactions.pop().flatten()

        winner = random.choice(users)
        await channel.send(f"Congrats, {winner.mention}! You just won the giveaway for {prize}!")
        await winner.send(f"You just won a giveaway in {ctx.guild.name} for {prize}!")


@giveaway.error 
async def giveaway_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Please provide all needed arguments! They are `channel`, `time` and `prize`")
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You need the `Giveaway Manager` role for this command to work, {ctx.author.mention}!")


@client.event 
async def on_message(msg : discord.Message):
    if msg.guild:
        return 
    else:
