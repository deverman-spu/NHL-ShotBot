import discord
import os
import requests
import pytz

from discord.ext import commands
from datetime import datetime, date

###### ONLY CHANGE THESE VALUES ######
prefix="%"
teamId="14"
### GET TEAM ID FROM INCLUDED FILE ###

bot = commands.Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print("Good to go!")
    print(bot.user)

@bot.command()
async def shots(ctx):
    '''
    Returns the shot count for the specified NHL game.
    '''
    date = str(datetime.now(pytz.timezone('America/Vancouver')).date())

    schedule = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=" + teamId +"&date=" + date

    try:
        req = requests.get(schedule)
        data = req.json()
    except requests.exceptions.RequestException as e: 
        print(e)
        await ctx.send("Error connecting to NHL API")


    if(data['totalGames'] > 0):
        gameId = str(data['dates'][0]['games'][0]['gamePk'])
        liveUrl = "https://statsapi.web.nhl.com/api/v1/game/" + gameId + "/feed/live"
        
        try:
            req = requests.get(liveUrl)
            data = req.json()
        except requests.exceptions.RequestException as e: 
            print(e)
            await ctx.send("Error connecting to NHL API")

        if(int(data['gameData']['status']['statusCode']) >= 3):
            home_team_name = data['gameData']['teams']['home']['triCode']
            home_team_shots = str(data['liveData']['boxscore']['teams']['home']['teamStats']['teamSkaterStats']['shots'])
            away_team_name = data['gameData']['teams']['away']['triCode']
            away_team_shots = str(data['liveData']['boxscore']['teams']['away']['teamStats']['teamSkaterStats']['shots'])
            period = data['liveData']['linescore']['currentPeriodOrdinal']
            timeleft = data['liveData']['linescore']['currentPeriodTimeRemaining']

            embed = discord.Embed(title="Shot Count", colour=discord.Colour(0x2704eb), description="------------------")
            embed.set_thumbnail(url="https://i.ibb.co/9hmxFhD/small-logo.png")

            if(timeleft == "END"):
                embed.set_footer(text=away_team_name + "  @  " + home_team_name + " -- " + period.upper() + " -- " + timeleft.upper())
            elif(timeleft == "Final"):
                embed.set_footer(text=away_team_name + "  @  " + home_team_name + " -- " +  timeleft.upper())
            else:
                embed.set_footer(text=away_team_name + "  @  " + home_team_name + " -- " + period.upper() + " -- " + timeleft + "  remaining.")

            embed.add_field(name=away_team_name, value=away_team_shots, inline=True)
            embed.add_field(name=home_team_name, value=home_team_shots, inline=True)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Game is not live yet.")
    else:
        await ctx.send("No game today.")

bot.run('<BOT TOKEN HERE>')