import discord
import os
import retrieveStats

from discord.ext import commands
from discord.ext.commands import CheckFailure
from dotenv import load_dotenv

#TODO: Make bot read from runner data doc so it auto updates, then make a command that reloads the bot
#so endpoint isn't spammed

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents, case_insensitive=True)
ADMINROLES = {"Moderator", "Developer"}
COMMANDSCHANNEL = int(os.getenv('DISCORD_COMMANDS_CHANNEL_ID'))
TESTCOMMANDCHANNEL = int(os.getenv('DISCORD_COMMANDS_CHANNEL_ID_TEST_REMOVE_AFTER_BETA'))
DATACHANNEL = int(os.getenv('DATA_CHANNEL_ID'))
ALLOWED_CHANNEL_IDS = [COMMANDSCHANNEL, TESTCOMMANDCHANNEL]

parsed_data = None

async def getProfileEmbed(profile):
    url = f"https://minotar.net/helm/{profile[0]}/{128}"

    embed = discord.Embed(title=f"{profile[0]}'s Stats",
                          color=discord.Color.blurple())
    embed.set_image(url=url)
    embed.add_field(name="IGN", value=profile[0])
    embed.add_field(name="PB", value=profile[2])
    embed.add_field(name="Classic PB", value=profile[1])

    return embed

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    bot.loop.create_task(retrieveStats.retrieve_pace(bot))

async def global_channel_check(ctx):
    if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
        raise CheckFailure("This command cannot be used in this channel.")
    return True

bot.check(global_channel_check)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send(error)
    else:
        await ctx.send(f"An error occurred: {str(error)}")

@bot.command(name='commands')
async def commands(ctx, *args):
    await ctx.send('```'
                   "!!profile stats <ign>\n"
                   "!!commands\n"
                   "!!classic\n"
                   "!!man\n"
                   '```')

@bot.command(name='classic')
async def classic(ctx, *args):
    await ctx.send('MAN')

@bot.command(name='test')
async def test(ctx, *args):
    await ctx.send('@Moderator')

@bot.command(name='man')
async def man(ctx, *args):
    await ctx.send('CLASSIC')

@bot.command(name='profile')
async def profile(ctx, action, *args):
    channel = bot.get_channel(DATACHANNEL)
    if channel is None:
        await ctx.send("Channel not found!")
        return

    async for msg in channel.history(limit=1):
        lines = msg.content[3:-3].strip().split('\n')
        parsed_data = [line.strip('<>').split(', ') for line in lines]
    if action == 'stats':
        if len(args) < 1:
            await ctx.send("Please provide an ign.")
            return

        ign = args[0]

        for profile in parsed_data:
            if profile[0] == ign:
                stats_embed = await getProfileEmbed(profile)
                await ctx.send(embed=stats_embed)
                break
        else:
            await ctx.send(f"Runner {ign} not found.")
    else:
        await ctx.send("Invalid command params")

# Run the bot with your token from the environment variable
bot.run(TOKEN)