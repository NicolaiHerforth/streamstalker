import discord
from dict import DictionaryReader
import logging, json, sys
from urllib.request import urlopen, Request
import _pickle as pickle


bot = discord.Client()

game = discord.Game("Spying on streamers!")

with open('users.txt', 'r') as user_file:
   users = json.loads(user_file.read())

#users = {"thezephan": "Zephan#0001", "calioqt": "caliotest#8702"}

print('Users loaded, type of variable:', type(users))
print(users)
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=game)

@bot.event
async def on_member_update(before, after):
    print(f'{after.name} changed status with the activity', after.activity)
    channel = 'bottest'



    if hasattr(after.activity, 'twitch_name') and not hasattr(before.activity, 'twitch_name'):
        streamer = after.activity.twitch_name
        curr_user = users[streamer]
        user_list = list(map(str, bot.users))
        indes = user_list.index(curr_user)
        role = discord.utils.get(before.guild.roles, name="Live")
        member_list = [*bot.get_all_members()]
        member = member_list[indes]
        print(streamer, 'started streaming, go watch at twitch.tv/' + streamer)
        role = discord.utils.get(before.guild.roles, name="Live")
        await member.add_roles(role)

        channel_gen = [*bot.get_all_channels()]
        channel_list = list(map(str, channel_gen))
        channel_index = channel_list.index(channel)
        tar_channel = channel_gen[channel_index]
        await tar_channel.send(f'{streamer} just started streaming. Go watch them at https://www.twitch.tv/{streamer}')

        

    
    elif hasattr(before.activity, 'twitch_name') and not hasattr(after.activity, 'twitch_name'):
        streamer = before.activity.twitch_name
        curr_user = users[streamer]
        user_list = list(map(str, bot.users))
        indes = user_list.index(curr_user)
        role = discord.utils.get(before.guild.roles, name="Live")
        member_list = [*bot.get_all_members()]
        member = member_list[indes]

        role = discord.utils.get(before.guild.roles, name="Live")
        try: 
            await member.remove_roles(role)
        except AttributeError:
            pass

        channel_gen = [*bot.get_all_channels()]
        channel_list = list(map(str, channel_gen))
        channel_index = channel_list.index(channel)
        tar_channel = channel_gen[channel_index]
        flattened =  await tar_channel.history(limit=20).flatten()
        msg_idx = []
        for message in flattened:
            if f'{streamer} just started streaming. Go watch them at https://www.twitch.tv/{streamer}' == message.content:
                msg_idx.append(flattened.index(message))

        for idx in msg_idx:
            await flattened[idx].delete()
    print()
    print()


@bot.event
async def on_message(message):
    channels = ["bottest"]
    if message.author == bot.user:
        return
    elif str(message.channel) in channels:
        if message.content.startswith('!addstreamer'):
            try:
                await message.channel.send(f'Adding streamer {message.content.split()[1]}')
                with open('users.txt','w') as user_file:
                    users[message.content.split()[1]] = message.content.split()[2]
                    json.dump(users, user_file)
            except IndexError:
                await message.channel.send("Remember to type twitch name first and then discord username!")

        # elif message.content.split()[0] in users.keys():
        #     await message.channel.send(f"{message.content.split()[0]}  just went live")
        #     curr_user = users[message.content.split()[0]]
        #     user_list = list(map(str, bot.users))
        #     indes = user_list.index(curr_user)
        #     role = discord.utils.get(message.guild.roles, name="Live")
        #     member_list = [*bot.get_all_members()]
        #     member = member_list[indes]
        #     print(member, type(member))
        #     await member.add_roles(role)
        # elif message.content.startswith("donkeyballs"):
        #     curr_user = users[message.content.split()[1]]
        #     user_list = list(map(str, bot.users))
        #     indes = user_list.index(curr_user)
        #     role = discord.utils.get(message.guild.roles, name="Live")
        #     member_list = [*bot.get_all_members()]
        #     member = member_list[indes] 
        #     await member.remove_roles(role)

"""
@bot.event
async def on_message(message):
    id = bot.get_guild('564553790074912769')
    channels = ["bottest"]
    if message.author == bot.user:
        return

    elif str(message.channel) in channels: # Check if in correct channel
        if message.content.split()[0] in users.values():
            await message.channel.send(f'Zephan just went live')
        else:
            print(message.content.split()[0])
        if message.content.startswith('!addstreamer'):
            await message.channel.send(f'Adding streamer {message.content.split()[1]}')
            with open('users.txt', encoding='utf-8','w') as user_file:
                users[]
                json.dump(users, user_file)
    
"""

"""
        if message.content.find("!hello") != -1:
            await message.channel.send("Zephan")
        elif message.content == "!zcommands":
            embed = discord.Embed(title="Info on ZephBot", description="Some useful commands")
            embed.add_field(name="!hello", value="Greets the user")
            embed.add_field(name="!botinfo", value="Prints description of bot")
            await message.channel.send(content=None, embed=embed)
        elif message.content == "!botinfo":
            await message.channel.send("This bot is supposed to track streamers, provide them with appropriate rank and announce when they go live. \nWhen they stop streaming, the rank should be withdrawn and the post should be removed.")
        elif message.content.startswith('!clear'):
            await message.channel.send( 'Clearing messages...')
"""

bot.run('NTY4MTMwOTY3MDY4MjEzMjg3.XLfUgA.LTV3cY7EOvnHeW5oYJ2oDxvYz0o')
