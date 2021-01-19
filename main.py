import os 

os.environ['MPLCONFIGDIR'] = 'matplotlib'

from replit import db
import discord
from discord.ext import commands
import asyncio
import  datetime as dt
from keep_alive import keep_alive
import matplotlib as mpl

mpl.use('Agg')

import matplotlib.pyplot as plt


intents = discord.Intents.default()
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix='!',intents=intents)

theTime = 60 # CHANGEABLE! TICK TIME.

for player in db:
  pier = db[player][:8] 

  # Here goes some database changing logic if we need one
  db[player]=pier

  # Debug log the database
  print(pier)



def getUserFromMention(mention):
    if mention.startswith('<@') and mention.endswith('>'):
        mention = mention[2: -1]
        if mention.startswith('!'):
            mention = mention[1:]
        return bot.get_user(int(mention))

def sorteg(a): #Fun sorting
    return a[1]



@bot.command(pass_context=True)  # Actual bot command
async def diagram(ctx, arg = None):  # Circlular diagram 

    # Get database key from author
    sender = str(ctx.message.author).split('#')[0]

    # If there is argument to command
    if arg is not None:
        # And it is working mention
        user = getUserFromMention(arg)
        # Then we research that instead
        if user is not None:
            # Get database key from mention
            sender = str(user).split('#')[0]

    # Check if the person is in the database and if there's pie data
    if sender not in db or 'pie' not in db[sender][7]:
        # Otherwise it doesn't work for us
        await ctx.send("Didn't find any data about you or the mentioned person!")
        return

    lab= []
    dat = []

    # Count total
    total = 0
    for j in db[sender][7]['pie'].keys():
      total+=db[sender][7]['pie'][j]

    # Extract data from the database
    for j in db[sender][7]['pie'].keys():
      # Sometimes there are unfun 'None's just flying around
      if j == 'None':
        continue

      currentData = db[sender][7]['pie'][j]

      # We don't show anything less then 3 % 
      if currentData/total <= 0.03:
        continue

      dat.append(currentData)
      lab.append(j)
    
    # Debug log it
    print(dat)
    print(lab)

    # Drawing the plot
    fig, ax = plt.subplots()
    ax.pie(dat,labels=lab,autopct='%1.1f%%',startangle=90)
    ax.axis('equal')

    #Saving and sending the picture
    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))



@bot.command(pass_context=True)  # Actual bot command
async def stats(ctx, arg = None):  # Global text stats

    message = ""

    # Extracting data from the database
    arr = [[i,sum(db[i][:7])]for i in db if '#' not in i]
    arr.sort(key=sorteg,reverse=True)

    # Formatting the data
    for i in arr:
        message += ';\n' + i[0] + ": " + str(i[1])
    message = message[2:]

    # Sending the data
    await ctx.send(message)



@bot.command(pass_context=True)  # Actual bot command
async def coolGraph(ctx, arg = None):  # Global text stats in graph variant
    
    # Extracting data from the database
    dat = sum([sum(db[i][:7])for i in db])
    arr = [[i,sum(db[i][:7])]for i in db if '#' not in i and sum(db[i][:7]) >= dat*0.03]  # Now only gets people who contibuted more than 3% total time
    arr.sort(key=sorteg,reverse=True)
    x = []
    y = []
    for i in arr:
        x.append(i[0])
        y.append(i[1])

    # Drawing the plot
    fig, ax = plt.subplots()
    ax.bar(x, y)

    ax.set_facecolor('seashell')
    fig.set_facecolor('floralwhite')
    fig.set_figwidth(12)
    fig.set_figheight(6)

    # Saving and sending the picture
    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))

@bot.command(pass_context=True) # Actual bot command
async def coolgraph(ctx,arg=None): # Lowercase analog
    await coolGraph(ctx,arg)



@bot.command(pass_context=True) # Actual bot command
async def personalGraph(ctx, arg = None): # Personal days of week graph

    # Get database key from author
    sender = str(ctx.message.author).split('#')[0]

    # If there is argument to command
    if arg is not None:
        # And it is working mention
        user = getUserFromMention(arg)
        # Then we research that instead
        if user is not None:
            # Get database key from mention
            sender = str(user).split('#')[0]

    # Check if the person is in the database 
    if sender not in db:
        # Otherwise it doesn't work for us
        await ctx.send("Didn't find any data about you or the mentioned person!")
        return

    # Extracting data from the database
    x = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
    y = db[sender][:7]

    # Drawing the plot
    fig, ax = plt.subplots()
    ax.bar(x, y)

    ax.set_facecolor('seashell')
    fig.set_facecolor('floralwhite')
    fig.set_figwidth(12)
    fig.set_figheight(6)

    # Saving and sending the picture
    plt.savefig("thing.png")
    await ctx.channel.send(file=discord.File("thing.png"))

@bot.command(pass_context=True) # Actual bot command
async def personalgraph(ctx,arg=None): # Lowercase analog
    await personalGraph(ctx,arg)



async def my_background_task(): # Just a tick based processing
    global theTime
    while True:
        # Get day of the week
        today = dt.datetime.now().weekday()

        for i in bot.get_all_channels():
            # Find all voice channels
            if str(i.type) == "voice":
              for j in i.members:
                
                # Get database key from member
                j = str(j).split('#')[0]

                # If there's no data in database, create
                if j not in db:
                    db[j] = [0]*7
                    r = db[j]
                    r.append({"pie":{}})
                    db[j]=r
                
                # Add elapsed time to the member's entry
                v = db[j]
                v[today]+=theTime
                db[j] = v

        alr = {}
        for i in bot.get_all_members():
            if i.bot:
              continue

            # Get database key from member
            player = str(i).split('#')[0]
            
            # We don't care about the person if there's no database entry or if already 
            # researched them
            if player not in db or player in alr:
              continue
            alr[player]=0

            # Get activity
            act = str(i.activity)

            # Standartizing the activity
            if act == 'Spotify':
              if i.activities.__len__() > 1:
                act = str(i.activities[1])
            if act == 'None':
              continue
            if "name='" in act:
              pd = act.find("name='")
              act = act[pd:].split("'")[1]
            
            # Add elapsed time to activity in member's entry
            pier = db[player]
            if act not in pier[7]['pie']:
              pier[7]['pie'][act]=0
            pier[7]['pie'][act]+=theTime
            db[player]=pier
        await asyncio.sleep(theTime)



keep_alive()

bot.loop.create_task(my_background_task())
bot.run(os.getenv('TOKEN'))