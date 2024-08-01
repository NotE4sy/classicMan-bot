import json
import discord
import retrieveStats


async def getProfileEmbed(profile):
    url = f"https://minotar.net/helm/{profile['ign']}/{128}"

    embed = discord.Embed(title=f"{profile['profileName']}'s Stats",
                          color=discord.Color.blurple())
    embed.set_image(url=url)
    embed.add_field(name="IGN", value=profile['ign'])
    embed.add_field(name="PB", value=retrieveStats.msConvert(profile['pb']))
    embed.add_field(name="Classic PB",
                    value=retrieveStats.msConvert(profile['classic pb']))
    embed.add_field(name="Completions", value=profile['completions'])

    return embed


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
