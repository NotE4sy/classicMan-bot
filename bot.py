#Import libraries
import os
import discord
import asyncio
import retrieveStats
import json
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
    
    #open classicman profiles
    with open('res/profiles.json', 'r') as file:
        profiles = json.load(file)

    user_message = message.content

    if user_message.startswith(command_prefix):
        inJson = False
        user_message = user_message[len(command_prefix):]

        user_message = user_message.split()

        print(user_message)

        match user_message[0].lower():
            case "profile":
                if len(user_message) >= 2:
                    match user_message[1]:
                        case 'add':
                            newUser = {
                                "profileName": user_message[2],
                                "ign": user_message[2],
                                "previousID": 0,
                                "completions": 0,
                                "pb": 8580000,
                                "classic pb": 8580000
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
                        case 'remove':
                            toBeRemoved = {
                                "profileName": user_message[2],
                                "ign": user_message[2],
                                "previousID": 0,
                                "completions": 0,
                                "pb": 8580000,
                                "classic pb": 8580000
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
                        case 'stats':
                            profileName = user_message[2]
                            print(profileName)

                            for profile in profiles:
                                if profile['profileName'] == profileName:
                                    #Get profile stats and convert to embed
                                    statsEmbed = await profileHandler.getProfileEmbed(profile)

                                    #Send to channel
                                    await message.channel.send(embed=statsEmbed)

                                    #Break for efficiency
                                    break
                        case 'edit':
                            if len(user_message) > 4:
                                profileName = user_message[4]

                                match user_message[2]:
                                    case 'profileName':
                                        await profileHandler.editProfile(profileName, 'profileName', user_message[3])
                                        await message.channel.send(f"Successfully changed {profileName}'s profile name to {user_message[3]}")
                                    case 'ign':
                                        await profileHandler.editProfile(profileName, 'ign', user_message[3])
                                        await message.channel.send(f"Successfully changed {profileName}'s minecraft ign to {user_message[3]}")
                                    case 'bastionPB':
                                        await profileHandler.editProfile(profileName, 'pb', user_message[3])
                                        await message.channel.send(f"Successfully changed {profileName}'s bastion pb to {user_message[3]}")
                                    case 'classicPB':
                                        await profileHandler.editProfile(profileName, 'classic pb', user_message[3])
                                        await message.channel.send(f"Successfully changed {profileName}'s classic pb to {user_message[3]}")
                                    case 'completions':
                                        await profileHandler.editProfile(profileName, 'completions', user_message[3])
                                        await message.channel.send(f"Successfully changed {profileName}'s no. completions to {user_message[3]}")
                                    case _:
                                        await message.channel.send("Invalid command params")
                            else:
                                await message.channel.send("Invalid command params")
                        case 'list':
                            classicTime = 3600000

                            if isinstance(profiles, list) and all(isinstance(profile, dict) for profile in profiles):
                                profilesSorted = sorted(profiles, key=lambda x: x.get('classic pb', 0))

                                print(profilesSorted)
                            else:
                                print("Profiles data is not in the expected format.")

                            for profile in profilesSorted:
                                if profile['classic pb'] < classicTime:
                                    classicTime = retrieveStats.msConvert(profile['classic pb'])
                                else:
                                    classicTime = "None"

                                await message.channel.send(
                                    '```'
                                    f'Profile name: {profile['profileName']}\n'
                                    f'Minecraft ign: {profile['ign']}\n'
                                    f'Classic pb: {classicTime}\n'
                                    '```'
                                )

                                classicTime = 100000
                        case _:
                            await message.channel.send("Invalid command params")

                else:
                    await message.channel.send("Invalid command params")
            case 'commands':
                await message.channel.send(
                    "```"
                    "!!profile add <profileName>\n"
                    "!!profile remove <profileName>\n"
                    "!!profile stats <profileName>\n"
                    "!!profile edit variable newValue <profileName>\n"
                    "!!commands"
                    "```"
                )
            case _:
                await message.channel.send("Invalid command params")

#Start bot
async def main():
    await client.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())