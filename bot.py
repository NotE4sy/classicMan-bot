import discord
from discord.ext import commands
import json
import os
import retrieveStats
import profileHandler

from dotenv import load_dotenv

# Set up intents (make sure to enable the message content intent in the Discord Developer Portal)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

# Set up the bot with a command prefix and intents
bot = commands.Bot(command_prefix='!!', intents=intents)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    bot.loop.create_task(retrieveStats.retrieve_pace(bot))

# Command: Profile management
@bot.command(name='profile')
async def profile(ctx, action, *args):
    with open('res/profiles.json', 'r') as file:
        profiles = json.load(file)

    if action == 'add':
        if len(args) < 1:
            await ctx.send("Please provide a profile name.")
            return

        new_user = {
            "profileName": args[0],
            "ign": args[0],
            "previousID": 0,
            "completions": 0,
            "pb": 8580000,
            "classic pb": 8580000
        }

        if any(profile['ign'] == new_user['ign'] for profile in profiles):
            await ctx.send(
                f"{new_user['profileName']} is already in classicman!")
        else:
            profiles.append(new_user)
            await ctx.send(
                f"Successfully added {new_user['profileName']} to classicman!")

        with open('res/profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)

    elif action == 'remove':
        if len(args) < 1:
            await ctx.send("Please provide a profile name.")
            return

        ign_to_remove = args[0]
        to_be_removed = None

        for profile in profiles:
            if profile["ign"] == ign_to_remove:
                to_be_removed = profile
                break

        if to_be_removed:
            profiles.remove(to_be_removed)
            await ctx.send(
                f"Successfully removed {to_be_removed['profileName']} from classicman!"
            )
        else:
            await ctx.send(f"{ign_to_remove} is not in classicman!")

        with open('res/profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)

    elif action == 'stats':
        if len(args) < 1:
            await ctx.send("Please provide a profile name.")
            return

        profile_name = args[0]

        for profile in profiles:
            if profile['profileName'] == profile_name:
                stats_embed = await profileHandler.getProfileEmbed(profile)
                await ctx.send(embed=stats_embed)
                break
        else:
            await ctx.send(f"Profile {profile_name} not found.")

    elif action == 'edit':
        if len(args) < 3:
            await ctx.send(
                "Please provide a variable, new value, and profile name.")
            return

        variable, new_value, profile_name = args[0], args[1], args[2]
        for profile in profiles:
            if profile['profileName'] == profile_name:
                if variable in profile:
                    profile[variable] = new_value
                    await ctx.send(
                        f"Successfully updated {variable} for {profile_name}.")
                else:
                    await ctx.send(f"Variable {variable} not found in profile."
                                   )
                break
        else:
            await ctx.send(f"Profile {profile_name} not found.")

        with open('res/profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)

    elif action == 'list':
        profiles_sorted = sorted(profiles,
                                 key=lambda x: x.get('classic pb', 0))
        message_content = ''

        for profile in profiles_sorted:
            classic_time = retrieveStats.ms_convert(
                profile['classic pb']
            )
            message_content += f"### Profile name: {profile['profileName']}\n"
            message_content += f"Minecraft ign: {profile['ign']}\n"
            message_content += f"Classic pb: {classic_time}\n\n"

        await ctx.send(message_content)

    else:
        await ctx.send("Invalid command params")


# Run the bot with your token from the environment variable
bot.run(TOKEN)