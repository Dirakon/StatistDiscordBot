import os 
os.environ['MPLCONFIGDIR'] = 'matplotlib'
from replit import db
import discord
from discord.ext import commands
import asyncio
#import requests
#import pandas as pd
import  datetime as dt
#import matplotlib as mtpl
from keep_alive import keep_alive
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

intents = discord.Intents.default()
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents
)
theTime = 60
for player in db:
  pier = db[player]
  db[player]=pier
  print(db[player])
guilder = None

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def diagram(ctx, arg = None):  # создаем асинхронную фунцию бота
    global guilder
    global channels
    sender = str(ctx.message.author).split('#')[0]
    if arg is not None:
        user = getUserFromMention(arg)
        if user is not None:
            sender = str(user).split('#')[0]
    if sender not in db or 'pie' not in db[sender][7]:
        await ctx.send("Didn't find any data about you!")
        return

    lab= []
    dat = []
    for j in db[sender][7]['pie'].keys():
      if j == 'None':
        continue
      dat.append(db[sender][7]['pie'][j])
      lab.append(j)
    print(dat)
    print(lab)
    fig, ax = plt.subplots()
    ax.pie(dat,labels=lab,autopct='%1.1f%%',startangle=90)
    ax.axis('equal')
    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))


@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def start(ctx, arg = None):  # создаем асинхронную фунцию бота
    global guilder
    if guilder is not None:
        await ctx.send("Session already started")
        return
    gld = ctx.guild
    guilder = gld


    await ctx.send("started tracking this server now!")

def sorteg(a):
    return a[1]


@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def stats(ctx, arg = None):  # создаем асинхронную фунцию бота
    global guilder
    message = ""
    arr = [[i,sum(db[i][:7])]for i in db if '#' not in i]
    arr.sort(key=sorteg,reverse=True)
    for i in arr:
        message += ';\n' + i[0] + ": " + str(i[1])
    message = message[2:]
    await ctx.send(message)

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def personalgraph(ctx,arg=None):
    await personalGraph(ctx,arg)
@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def coolgraph(ctx,arg=None):
    await coolGraph(ctx,arg)
@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def coolGraph(ctx, arg = None):  # создаем асинхронную фунцию бота
    global guilder
    arr = [[i,sum(db[i][:7])]for i in db if '#' not in i]
    arr.sort(key=sorteg,reverse=True)
    x = []
    y = []
    for i in arr:
        x.append(i[0])
        y.append(i[1])
    fig, ax = plt.subplots()

    ax.bar(x, y)

    ax.set_facecolor('seashell')
    fig.set_facecolor('floralwhite')
    fig.set_figwidth(12)
    fig.set_figheight(6)

    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))

def getUserFromMention(mention):
    if mention.startswith('<@') and mention.endswith('>'):
        mention = mention[2: -1]
        if mention.startswith('!'):
            mention = mention[1:]
        return bot.get_user(int(mention))

@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def personalGraph(ctx, arg = None):  # создаем асинхронную фунцию бота
    global guilder
    global channels
    sender = str(ctx.message.author).split('#')[0]
    if arg is not None:
        user = getUserFromMention(arg)
        if user is not None:
            sender = str(user).split('#')[0]
    if sender not in db:
        await ctx.send("Didn't find any data about you!")
        return
    x = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
    y = db[sender][:7]
    fig, ax = plt.subplots()
    ax.bar(x, y)

    ax.set_facecolor('seashell')
    fig.set_facecolor('floralwhite')
    fig.set_figwidth(12)
    fig.set_figheight(6)

    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))




async def my_background_task():
    global guilder
    global channels
    global theTime
    today = dt.datetime.now().weekday()
    while guilder is None:
        await asyncio.sleep(1)
    while True:
        chans = guilder.channels

        for i in chans:
            if str(i.type) == "voice":
              for j in i.members:
                j = str(j).split('#')[0]
                #print(db[j])
                if j not in db:
                    db[j] = [0]*7
                v =  db[j]
                v.append({"pie":{}})
                v[today]+=theTime
                db[j] = v
        for i in guilder.members:
            if i.bot:
              continue
            player = str(i).split('#')[0]
            if player not in db:
              continue
            act = str(i.activity)
            if act == 'Spotify':
              if i.activities.__len__() > 1:
                act = str(i.activities[1])
            if act == 'None':
              continue
            if "name='" in act:
              pd = act.find("name='")
              act = act[pd:].split("'")[1]
            pier = db[player]
            if act not in pier[7]['pie']:
              pier[7]['pie'][act]=0
            pier[7]['pie'][act]+=theTime
           # print(act)
            db[player]=pier
        await asyncio.sleep(theTime)
keep_alive()

bot.loop.create_task(my_background_task())
bot.run(os.getenv('TOKEN'))