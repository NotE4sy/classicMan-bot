#Import libraries
import os
import discord
import asyncio
import retrieveStats
import json
import math
import profileHandler

from discord import Intents, Client, Message
from dotenv import load_dotenv

#Misc
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = Intents.default()
intents.message_content = True

command_prefix = '!!'

client = discord.Client(intents=intents)

#open classicman profiles
with open('res/profiles.json', 'r') as file:
    profiles = json.load(file)

#main code
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running! :D')

    #begin retrieving pace
    client.loop.create_task(retrieveStats.retrievePace(client))

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    user_message = message.content

    if user_message.startswith(command_prefix):
        inJson = False
        user_message = user_message[len(command_prefix):]
        print(user_message)

        #Adding profiles to classicman
        if user_message[:11].lower() == "addprofile ":
            newUser = {
                "profileName": user_message[11:],
                "ign": user_message[11:],
                "previousID": 0,
                "completions": 0,
                "pb": 0,
                "classic pb": 0
            }
            
            for runner in profiles:
                if runner == newUser:
                    inJson = True

            if not inJson:
                profiles.append(newUser)
                await message.channel.send(f"Successfully added {newUser['profileName']} to classicman!")
            else:
                await message.channel.send(f"{newUser['profileName']} is already in classicman!")

            with open('res/profiles.json', 'w') as file:
                json.dump(profiles, file, indent=4)

        #Removing profiles from classicman
        elif user_message[:14].lower() == "removeprofile ":
            toBeRemoved = {
                "profileName": user_message[14:],
                "ign": user_message[14:],
                "previousID": 0,
                "completions": 0,
                "pb": 0,
                "classic pb": 0
            }

            for profile in profiles:
                if profile["ign"] == toBeRemoved['ign']:
                    inJson = True
                    toBeRemoved['previousID'] = profile['previousID']
                    toBeRemoved['completions'] = profile['completions']
                    toBeRemoved['pb'] = profile['pb']

            if inJson:
                profiles.remove(toBeRemoved)
                await message.channel.send(f"Successfully removed {toBeRemoved['profileName']} from classicman!")
            else:
                await message.channel.send(f"{toBeRemoved['profileName']} is not in classicman!")

            with open('res/profiles.json', 'w') as file:
                json.dump(profiles, file, indent=4)

        #View profile stats
        elif user_message[:6].lower() == "stats ":
            profileName = user_message[6:]
            print(profileName)

            for profile in profiles:
                if profile['profileName'] == profileName:
                    #Get profile stats and convert to embed
                    statsEmbed = profileHandler.getProfileEmbed(profile=profile)

                    #Send to channel
                    await message.channel.send(embed=statsEmbed)

                    #Break for efficiency
                    break

#Start bot
async def main():
    await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())