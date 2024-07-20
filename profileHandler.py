import json
import discord
import retrieveStats

with open('res/profiles.json', 'r') as file:
    profiles = json.load(file)

def getProfileEmbed(profile):
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