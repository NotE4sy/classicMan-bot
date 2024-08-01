import requests
import os
import json
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

async def retrieve_pace(bot: commands.Bot):
    channel = bot.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))

    # Open classicman profiles
    with open('res/profiles.json', 'r') as file:
        profiles = json.load(file)

    while True:
        for profile in profiles:
            # Getting response from API endpoint
            response = requests.get(runs_url,
                                    params={
                                        'name': profile['ign'],
                                        'hours': 1,
                                        'limit': 1
                                    })

            if response.status_code == 200:
                run = response.json()
                if run:
                    if 'first_portal' in run[0] and run[0][
                            'first_portal'] is not None and profile[
                                'previousID'] != run[0][
                                    'id'] and 'bastion' in run[0] and run[0][
                                        'bastion'] is None:
                        profile['previousID'] = run[0]['id']
                        enter_time = ms_convert(run[0]['first_portal'])

                        with open('res/profiles.json', 'w') as file:
                            json.dump(profiles, file, indent=4)

                        if channel:
                            rod_count = 0
                            pearl_count = 0
                            get_world_response = requests.get(
                                url=f"{world_url}?worldId={run[0]['id']}")
                            get_liveruns_response = requests.get(
                                url=liveruns_url)
                            live_msg = ""

                            if get_world_response.status_code == 200 and get_liveruns_response.status_code == 200:
                                world_data = get_world_response.json()
                                liveruns_data = get_liveruns_response.json()

                                for data in liveruns_data:
                                    if data['nickname'] == profile['ign']:
                                        rod_count = data['itemData'][
                                            'estimatedCounts'][
                                                'minecraft:blaze_rod']
                                        pearl_count = data['itemData'][
                                            'estimatedCounts'][
                                                'minecraft:ender_pearl']
                                        break

                                if world_data['isLive'] is True and world_data[
                                        'data']['vodId'] is not None:
                                    live_msg = f"[{profile['profileName']}](<http://twitch.tv/{world_data['data']['vodId']}>)"
                                else:
                                    live_msg = f"Offline - {profile['profileName']} (ign: {profile['ign']})"

                                await channel.send(
                                    f"## {enter_time} - First Portal (Bastionless)\n\n"
                                    f'{live_msg} <t:{int(time.time())}:R>\n'
                                    f'{ender_pearl_emote} {pearl_count} {blaze_rod_emote} {rod_count}'
                                )
                        else:
                            print("Channel not found.")

                        # Handling completions
                        if 'finish' in run[0] and run[0]['finish'] is not None:
                            message = ""
                            profile['completions'] += 1

                            # Handling PBs
                            if 'bastion' in run[0] and run[0][
                                    'bastion'] is None:
                                # Classic PBs
                                if run[0]['finish'] < profile['classic pb']:
                                    profile['classic pb'] = run[0]['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new classic pb of: {profile['classic pb']}!"
                            else:
                                # Bastion PBs
                                if run[0]['finish'] < profile['pb']:
                                    profile['pb'] = run[0]['finish']
                                    message = f"{profile['profileName']} ({profile['ign']}) has just gotten a new bastion pb of: {profile['pb']}!"

                            await channel.send(message)
                    # Preventing too much spam and function crashing
                    await asyncio.sleep(25)
                else:
                    print("No recent runs")
            else:
                print(f"Failed to fetch data: {response.status_code}")

            await asyncio.sleep(1)
