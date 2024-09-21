import os
import discord
import sqlite3

from dotenv import load_dotenv
load_dotenv()
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='/', description='BathBot commands', intents=intents)

GUILDID = os.getenv('GUILD_ID')




#bot stuff

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    # Database stuff
    try:
        os.remove("bathbase.db")
        print("clearing bathbase")
    except:
        print("bathbase not found!")

    print("creating bathbase")
    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    cur.execute("""CREATE TABLE usermoney(
                userID INTEGER PRIMARY KEY,
                money INTEGER DEFAULT 0)""")
    cur.execute("""CREATE TABLE inventory(
                userID INTEGER PRIMARY KEY,
                items TEXT)""")
    con.commit()
    con.close()

@bot.command()
async def inventory(ctx):
    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    user = ctx.message.author.id
    print(f"id: {user}")

    # initialize if user is not initialized
    if cur.execute("SELECT COUNT(*) FROM inventory WHERE userID = ?", (user,)).fetchall() == [(0,)]:
        print(" not found, init")
        cur.execute("INSERT INTO inventory (userID, items) VALUES (?, ?)", (user, ""))
        con.commit()

    currentinventory = cur.execute("SELECT items FROM inventory WHERE userID = ?", (user,)).fetchone()[0]

    # format inventory
    currentinventory = currentinventory.split('/')

    outputstring = ""
    for item in currentinventory:
        outputstring += item + "\n"

    await ctx.send(f"----\n${outputstring}\n----")
    con.commit()
    con.close()

@bot.command()
async def itemget(ctx, item):
    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    user = ctx.message.author.id
    print(f"id: {user}")

    # initialize if user is not initialized
    if cur.execute("SELECT COUNT(*) FROM inventory WHERE userID = ?", (user,)).fetchall() == [(0,)]:
        print(" not found, init")
        cur.execute("INSERT INTO inventory (userID, items) VALUES (?, ?)", (user, ""))
        con.commit()

    currentinventory = cur.execute("SELECT items FROM inventory WHERE userID = ?", (user,)).fetchone()[0]
    currentinventory += "/" + item.replace("/","_")
    cur.execute("DELETE FROM inventory WHERE userID = ?", (user))
    cur.execute("INSERT INTO inventory (userID, items) VALUES (?, ?)", (user, currentinventory))

    await ctx.send("Obtained " + item)

    con.commit()
    con.close()

@bot.command()
async def itemremove(ctx, item):
    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    user = ctx.message.author.id
    print(f"id: {user}")

    # initialize if user is not initialized
    if cur.execute("SELECT COUNT(*) FROM inventory WHERE userID = ?", (user,)).fetchall() == [(0,)]:
        print(" not found, init")
        cur.execute("INSERT INTO inventory (userID, items) VALUES (?, ?)", (user, ""))
        con.commit()

    currentinventory = cur.execute("SELECT items FROM inventory WHERE userID = ?", (user,)).fetchone()[0]
    
    if currentinventory.find(item) == -1:
        await ctx.send("Item not found! Use /inventory to view your items")
        con.commit()
        con.close()
        return

    currentinventory = currentinventory.replace("/"+item, "")

    cur.execute("DELETE FROM inventory WHERE userID = ?", (user))
    cur.execute("INSERT INTO inventory (userID, items) VALUES (?, ?)", (user, currentinventory))

    await ctx.send("Removed " + item)
    
    con.commit()
    con.close()



@bot.command()
async def payday(ctx):
    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    user = ctx.message.author.id
    print(f"id: {user}")

    # initialize if user is not initialized
    #print(cur.execute("SELECT COUNT(*) FROM usermoney WHERE user = ?", (user,)).fetchall())
    if cur.execute("SELECT COUNT(*) FROM usermoney WHERE userID = ?", (user,)).fetchall() == [(0,)]:
        print(" not found, init")
        cur.execute("INSERT INTO usermoney (userID, money) VALUES (?, ?)", (user, 0))
        con.commit()

    oldmoney = cur.execute("SELECT money FROM usermoney WHERE userID = ?", (user,)).fetchone()[0]
    print(oldmoney)
    cur.execute("UPDATE usermoney SET money = ? WHERE userID = ?", (int(oldmoney)+1, user))
    con.commit()

    # Retrieve the updated money value
    updated_money = cur.execute("SELECT money FROM usermoney WHERE userID = ?", (user,)).fetchone()[0]

    await ctx.send(f"Your cash sire: ${updated_money}")
    con.close()

@bot.command()
async def gamble(ctx, *amount: int):

    if len(amount) != 1:
        await ctx.send(f"wrong args")
        return
    amount = int(amount[0])
    print(f"amount: {amount}")

    con = sqlite3.connect("bathbase.db")
    cur = con.cursor()

    user = ctx.message.author.id
    print(f"id: {user}")

    if cur.execute("SELECT COUNT(*) FROM usermoney WHERE userID = ?", (user,)).fetchall() == [(0,)]:
        print(" not found, init")
        cur.execute("INSERT INTO usermoney (userID, money) VALUES (?, ?)", (user, 0))
        con.commit()

    oldmoney = cur.execute("SELECT money FROM usermoney WHERE userID = ?", (user,)).fetchone()[0]
    print(oldmoney)

    if random.random()*100 < 50:
        cur.execute("UPDATE usermoney SET money = ? WHERE userID = ?", (int(oldmoney)+amount, user))
        await ctx.send(f"You win! Balance: {oldmoney+amount}")
    else:
        cur.execute("UPDATE usermoney SET money = ? WHERE userID = ?", (int(oldmoney)-amount, user))
        await ctx.send(f"You LOSE fuckhead! Balance: {oldmoney-amount}")
    con.commit()
    con.close()


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)