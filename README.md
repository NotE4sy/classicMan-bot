# classicMan-bot
A discord bot for classic mcsr

Commands:

All commands of this bot will have a prefix of '!!' which can be changed in the bot.py file

!!addprofile name:

Adds a new profile to classicMan

Basic structure:
{
  "profileName": name,
  "ign": ign,
  "previousID": 0,
  "completions": 0,
  "pb": pb,
  "classic pb": classic pb
}

Adding a new profile will set profileName and ign to the name set

!!removeprofile profileName:

Removes the profile with profileName

!!stats profileName

returns the stats of the profile with profileName in an embed
