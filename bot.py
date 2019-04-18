import discord
import logging, json, sys, os
import _pickle as pickle
from dict import DictionaryReader
from urllib.request import urlopen, Request


bot = discord.Client()
game = discord.Game("Spying on streamers!")


@bot.event
async def on_guild_join(guild):
    print(guild.name)

#users = {"thezephan": "Zephan#0001", "calioqt": "caliotest#8702"}


@bot.event
async def on_ready():
    all_guilds = []
    print('ALL GUILDS\n', bot.guilds)
    global users
    for g in bot.guilds:
        if g not in all_guilds:
            all_guilds.append(g)
    for guild in all_guilds:
        if not os.path.isfile(f'usrs/users-{guild.id}.txt'):
            print(f'User file does not exist, creating for {guild.name}')
            users = {}
            with open(f'usrs/users-{guild.id}.txt', 'w+') as user_file:
                json.dump(users, user_file)
        else:
            print(f'Userfile for {guild.name} exists')

        if not os.path.isfile(f'channels/channel-{guild.id}.txt'):
            print(f'Channel file on {guild.name} file does not exist, creating file for {guild.name}')
            channel = 'general' 
            with open(f'channels/channel-{guild.id}.txt', 'w+') as channel_file:
                channel_file.write(channel)
        else:
            print(f'Channel file for {guild.name} exists')

    
    await bot.change_presence(status=discord.Status.idle, activity=game)





@bot.event  
async def on_member_update(before, after):
    print(f'{after.name} changed status with the activity', after.activity)
    with open(f'usrs/users-{before.guild.id}.txt', 'r') as user_file:
        users = json.loads(user_file.read())
    
    with open(f'channels/channel-{before.guild.id}.txt', 'r') as channel_file:
        print('Reading Channel')
        channel = channel_file.read().split('\n')[0]
        print(channel)

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
    with open(f'usrs/users-{message.guild.id}.txt', 'r') as user_file:
        users = json.loads(user_file.read())

    with open(f'channels/channel-{message.guild.id}.txt', 'r') as channel_file:
        channels = channel_file.read().split('\n')
    
    if message.author == bot.user:
        return
    elif str(message.channel) in channels:
        if message.content.startswith('!addstreamer'):
            try:
                await message.channel.send(f'Adding streamer {message.content.split()[1]}')
                with open(f'usrs/users-{message.guild.id}.txt','w') as user_file:
                    users[message.content.split()[1]] = message.content.split()[2]
                    json.dump(users, user_file)
            except IndexError:
                await message.channel.send("Remember to type twitch name first and then discord username!")

        elif message.content.startswith('!streamers'):
            all_streamers = list(users.keys())
            await message.channel.send(f'All streamers connected are:\n{all_streamers}')
                
        elif message.content.startswith('!setchannel'):
            if len(message.content.split()) > 2:
                await message.channel.send('Channel names has to be one word!')
            else:
                channel_gen = [*bot.get_all_channels()]
                channel_list = list(map(str, channel_gen))
                new_channel = str(message.content.split()[1])
                if new_channel not in channel_list:
                    await message.channel.send(f'{new_channel} does not exist, please make sure the channel name is correct!')
                else:
                    await message.channel.send(f'Channel name set to {new_channel}')
                    with open(f'channels/channel-{message.guild.id}.txt', 'w') as channel_file:
                        channel_file.write(new_channel)
        elif message.content.startswith('!sscommands'):
            embed = discord.Embed(title="Commands for StreamStalker", description="Some useful commands")
            embed.add_field(name="!addstreamer", value="Adds streamer to the list of streamers")
            embed.add_field(name="!streamers", value="Lists all current registered streamers")
            embed.add_field(name="!setchannel", value="Sets what channel StreamStalker should work in")
            await message.channel.send(content=None, embed=embed)


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
    channels = ["streaming"]
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
