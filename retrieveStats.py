import requests
import os
import math
import asyncio
import discord
import time

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

def ms_convert(millis):
    seconds = millis / 1000
    minutes = seconds / 60
    seconds = seconds % 60
    return f"{math.floor(minutes)}:{math.floor(seconds):02}"

runs_url = 'https://paceman.gg/stats/api/getRecentRuns/'
world_url = 'https://paceman.gg/stats/api/getWorld/'
liveruns_url = "https://paceman.gg/api/ars/liveruns"
ender_pearl_emote = "<:pearl:1265508441632407605>"
blaze_rod_emote = "<:rod:1265507954157949061>"

blinds = []
strongholds = []
enter_ends = []
completions = []

DATACHANNEL = int(os.getenv('DATA_CHANNEL_ID'))

async def retrieve_pace(bot: commands.Bot):
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    parsed_data = None
    while True:
        dataChannel = bot.get_channel(DATACHANNEL)

        async for msg in dataChannel.history(limit=1):
            lines = msg.content[3:-3].strip().split('\n')
            parsed_data = [line.strip('<>').split(', ') for line in lines]
        
        for profile in parsed_data:
            response = requests.get(runs_url, params={'name': profile[0], 'hours': 1, 'limit': 1})
            if response.status_code == 200:
                run = response.json()
                if run:
                    if 'bastion' in run[0] and run[0]['bastion'] is None:
                        if 'first_portal' in run[0] and run[0]['first_portal'] is not None and run[0]['id'] not in blinds:
                            blinds.append(run[0]['id'])
                            enter_time = ms_convert(run[0]['first_portal'])
                            if channel:
                                rod_count = 0
                                pearl_count = 0
                                get_world_response = requests.get(url=f"{world_url}?worldId={run[0]['id']}")
                                get_liveruns_response = requests.get(url=liveruns_url)
                                live_msg = ""
                                if get_world_response.status_code == 200 and get_liveruns_response.status_code == 200:
                                    world_data = get_world_response.json()
                                    liveruns_data = get_liveruns_response.json()
                                    for data in liveruns_data:
                                        if data['nickname'] == profile[0]:
                                            rod_count = data['itemData']['estimatedCounts']['minecraft:blaze_rod']
                                            pearl_count = data['itemData']['estimatedCounts']['minecraft:ender_pearl']
                                            break
                                    if world_data['isLive'] is True and world_data['data']['vodId'] is not None:
                                        live_msg = f"[{profile[0]}](<http://twitch.tv/{world_data['data']['twitch']}>)"
                                    else:
                                        live_msg = f"Offline - {profile[0]}"
                                    await channel.send(f"## {enter_time} - First Portal (Bastionless)\n\n{live_msg}  <t:{int(time.time())}:R>\n{ender_pearl_emote} {pearl_count} {blaze_rod_emote} {rod_count}")
                            else:
                                print("Channel not found.")

                        if 'stronghold' in run[0] and run[0]['stronghold'] is not None and run[0]['id'] not in strongholds:
                            strongholds.append(run[0]['id'])
                            enter_time = ms_convert(run[0]['stronghold'])
                            if channel:
                                get_world_response = requests.get(url=f"{world_url}?worldId={run[0]['id']}")
                                get_liveruns_response = requests.get(url=liveruns_url)
                                live_msg = ""
                                if get_world_response.status_code == 200 and get_liveruns_response.status_code == 200:
                                    world_data = get_world_response.json()
                                    liveruns_data = get_liveruns_response.json()

                                    if world_data['isLive'] is True and world_data['data']['vodId'] is not None:
                                        live_msg = f"[{profile[0]}](<http://twitch.tv/{world_data['data']['twitch']}>)"
                                    else:
                                        live_msg = f"Offline - {profile[0]}"
                                    await channel.send(f"## {enter_time} - Enter Stronghold (Bastionless)\n\n{live_msg}  <t:{int(time.time())}:R>\n")
                            else:
                                print("Channel not found.")

                        if 'end' in run[0] and run[0]['end'] is not None and run[0]['id'] not in enter_ends:
                            enter_ends.append(run[0]['id'])
                            enter_time = ms_convert(run[0]['end'])
                            if channel:
                                rod_count = 0
                                pearl_count = 0
                                get_world_response = requests.get(url=f"{world_url}?worldId={run[0]['id']}")
                                get_liveruns_response = requests.get(url=liveruns_url)
                                live_msg = ""
                                if get_world_response.status_code == 200 and get_liveruns_response.status_code == 200:
                                    world_data = get_world_response.json()
                                    liveruns_data = get_liveruns_response.json()
                                
                                    if world_data['isLive'] is True and world_data['data']['vodId'] is not None:
                                        live_msg = f"[{profile[0]}](<http://twitch.tv/{world_data['data']['twitch']}>)"
                                    else:
                                        live_msg = f"Offline - {profile[0]}"
                                    await channel.send(f"## {enter_time} - Enter End (Bastionless)\n\n{live_msg}  <t:{int(time.time())}:R>\n")
                            else:
                                print("Channel not found.")
                            
                    if 'finish' in run[0] and run[0]['finish'] is not None and run[0]['id'] not in completions:
                        completions.append(run[0]['id'])
                        
                        get_world_response = requests.get(url=f"{world_url}?worldId={run[0]['id']}")
                        get_liveruns_response = requests.get(url=liveruns_url)

                        if get_world_response.status_code == 200 and get_liveruns_response.status_code == 200:
                            world_data = get_world_response.json()
                            liveruns_data = get_liveruns_response.json()

                            if world_data['isLive'] is True and world_data['data']['vodId'] is not None:
                                live_msg = f"[{profile[0]}](<http://twitch.tv/{world_data['data']['twitch']}>)"
                            else:
                                live_msg = f"Offline - {profile[0]}"
                        
                            if 'bastion' in run[0] and run[0]['bastion'] is None:
                                await channel.send(f"## {ms_convert(run[0]['finish'])} - Finish (Bastionless)\n\n{live_msg}  <t:{int(time.time())}:R>\n")
                                minutes, seconds = map(int, profile[1].split(':'))
                                if run[0]['finish'] < (minutes * 60 + seconds) * 1000:
                                    profile[1] = str(run[0]['finish'])
                                    await channel.send(f"{profile[0]} has just gotten a new classic pb of: {profile[1]}!")
                            else:
                                minutes, seconds = map(int, profile[2].split(':'))
                                if run[0]['finish'] < (minutes * 60 + seconds) * 1000:
                                    profile[2] = str(run[0]['finish'])
                                    
                    await asyncio.sleep(25)
                else: 
                    print("No recent runs")
            else: 
                print(f"Failed to fetch data: {response.status_code}")
            await asyncio.sleep(1)