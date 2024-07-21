import json
import discord
import retrieveStats

async def getProfileEmbed(profile):
    print("H")
    url = f"https://minotar.net/helm/{profile['ign']}/{128}"
            
    #Create an embed for stats
    statsEmbed = discord.Embed(
                title=f"{profile['profileName']}'s stats:",
                color=discord.Color.blurple()
            )

    #Adding necessary information to the embed
    statsEmbed.set_image(url=url)
    statsEmbed.add_field(name="Minecraft ign", value=profile['ign'], inline=False)
    statsEmbed.add_field(name="Bastion pb: ", value=retrieveStats.msConvert(profile['pb']), inline=False)
    statsEmbed.add_field(name="Classic pb: ", value=retrieveStats.msConvert(profile['classic pb']), inline=False)
    statsEmbed.add_field(name="No. Completions: ", value=profile['completions'], inline=False)

    return statsEmbed

async def editProfile(profileName, variable, newVal: str):
    #open classicman profiles (read)
    with open('res/profiles.json', 'r') as file:
        profiles = json.load(file)

    #find correct profile
    for profile in profiles:
        if profile['profileName'] == profileName:
            #change value of variable to new value
            if variable == 'pb' or variable == 'classic pb' or variable == 'completions':
                newVal = int(newVal)

            profile[variable] = newVal

            #open classicman profiles (write)
            with open('res/profiles.json', 'w') as file:
                json.dump(profiles, file, indent=4)
            break