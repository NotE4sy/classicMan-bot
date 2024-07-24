#Import libraries
import requests
import os
import json
import math
import asyncio
import discord
import time

#Convert milliseconds to minutes and seconds
def msConvert(millis):
    seconds = millis / 1000
    minutes = seconds / 60
    seconds = seconds % 60
    return f"{math.floor(minutes)}:{math.floor(seconds):02}"

#paceman api url
runsUrl = 'https://paceman.gg/stats/api/getRecentRuns/'
worldUrl = 'https://paceman.gg/stats/api/getWorld/'
liverunsUrl = "https://paceman.gg/api/ars/liveruns"

ender_pearl_emote = "<:ender_pearl:1249639829252345916>"
blaze_rod_emote = "<:blaze_rod:1249633180378464381>"

#open classicman profiles
with open('res/profiles.json', 'r') as file:
    profiles = json.load(file)

#main function to retrieve paceman pace
async def retrievePace(client: discord.Client):
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    while True:
        for profile in profiles:
            #getting response from api endpoint
            response = requests.get(runsUrl, params={'name': profile['ign'], 'hours': 1, 'limit': 1})

            if response.status_code == 200:
                run = response.json()
                if run:
                    #If player has entered nether (TODO: Will change to first portal after bot is done)
                    if 'first_portal' in run[0] and run[0]['first_portal'] is not None and profile['previousID'] != run[0]['id'] and 'bastion' in run[0] and run[0]['bastion'] is None:
                        profile['previousID'] = run[0]['id']
                        enter_time = msConvert(run[0]['first_portal'])

                        with open('res/profiles.json', 'w') as file:
                            json.dump(profiles, file, indent=4)

                        if channel:
                            rodCount = 0
                            pearlCount = 0
                            getWorldResponse = requests.get(url=f"{worldUrl}?worldId={run[0]['id']}")
                            getliverunsResponse = requests.get(url=liverunsUrl)
                            liveMsg = ""

                            if getWorldResponse.status_code == 200 and getliverunsResponse.status_code == 200:
                                worldData = getWorldResponse.json()
                                liverunsData = getliverunsResponse.json()
                                print(worldData)
                                print(liverunsData)

                                for data in liverunsData:
                                    if data['nickname'] == profile['ign']:
                                        rodCount = data['itemData']['estimatedCounts']['minecraft:blaze_rod']
                                        pearlCount = data['itemData']['estimatedCounts']['minecraft:ender_pearl']
                                        break

                                if worldData['isLive'] is True and worldData['data']['vodId'] is not None:
                                    liveMsg = f"[{profile['profileName']}](<http://twitch.tv/{worldData['data']['vodId']}>)"
                                else:
                                    liveMsg = f"Offline - {profile['profileName']} (ign: {profile['ign']})"

                                await channel.send(
                                    f"## {enter_time} - First Portal (Bastionless)\n\n"
                                    f'{liveMsg} <t:{int(time.time())}:R>\n'
                                    f'{ender_pearl_emote}{pearlCount} {blaze_rod_emote}{rodCount}'
                                )
                        else:
                            print("Channel not found.")
                        
                        #Handling completions
                        if 'finish' in run[0] and run[0]['finish'] is not None:
                            profile['completions'] += 1

                            #Handling pbs
                            if 'bastion' in run[0] and run[0]['bastion'] is None:
                                #Classic pbs
                                if run[0]['finish'] < profile['classic pb']:
                                    profile['classic pb'] = run[0]['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new classic pb of: {profile['classic pb']}!"
                            else:
                                #Bastion pbs
                                if run[0]['finish'] < profile['pb']:
                                    profile['pb'] = run[0]['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new bastion pb of: {profile['pb']}!"          

                            channel.send(message)
                    #Preventing to much spam and function crashing
                    await asyncio.sleep(25)
                else:
                    print("No recent runs")
            else:
                print(f"Failed to fetch data: {response.status_code}")
            
            await asyncio.sleep(1)