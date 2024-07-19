#Import libraries
import requests
import os
import json
import math
import asyncio
import discord

#Convert milliseconds to minutes and seconds
def msConvert(millis):
    seconds = millis / 1000
    minutes = seconds / 60
    seconds = seconds % 60
    return f"{math.floor(minutes)}:{math.floor(seconds):02}"

#paceman api url
url = 'https://paceman.gg/stats/api/getRecentRuns/'

#open classicman profiles
with open('profiles.json', 'r') as file:
    profiles = json.load(file)

#main function to retrieve paceman pace
async def retrievePace(client: discord.Client):
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    while True:
        for profile in profiles:
            #getting response from api endpoint
            response = requests.get(url, params={'name': profile['ign'], 'hours': 1, 'limit': 1})

            if response.status_code == 200:
                jsonResponse = response.json()
                if isinstance(jsonResponse, list):
                    for run in jsonResponse:
                        #If player has entered nether (TODO: Will change to first portal after bot is done)
                        if 'nether' in run and run['nether'] is not None and profile['previousID'] != run['id']:
                            profile['previousID'] = run['id']
                            enter_time = msConvert(run['nether'])
                            message = f"{profile['profileName']} ({profile['ign']}) has entered the Nether at {enter_time}!"

                            if channel:
                                await channel.send(message)
                            else:
                                print("Channel not found.")
                        
                        #Handling completions
                        if 'finish' in run and run['finish'] is not None:
                            profile['completions'] += 1

                            #Handling pbs
                            if 'bastion' in run and run['bastion'] is None:
                                #Classic pbs
                                if run['finish'] < profile['classic pb']:
                                    profile['classic pb'] = run['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new classic pb of: {profile['classic pb']}!"
                            else:
                                #Bastion pbs
                                if run['finish'] < profile['pb']:
                                    profile['pb'] = run['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new bastion pb of: {profile['pb']}!"          

                                channel.send(message)
                        
                        #Preventing to much spam and function crashing
                        await asyncio.sleep(25)
                else:
                    print("Unexpected response format.")
            else:
                print(f"Failed to fetch data: {response.status_code}")
            
            await asyncio.sleep(1)
