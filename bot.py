import discord
import logging, json, sys, os
import _pickle as pickle
import time
from dict import DictionaryReader
from urllib.request import urlopen, Request



# Global variables used throughout all methods
token = os.environ.get('ENGLISH_DISCORD_TOKEN')
authorized_keys = os.environ.get('AUTHORIZED_KEYS')
bot = discord.Client()
game = discord.Game("Spying on streamers!")
cwd = sys.path[0]

# Server authentication load
authorized_servers = []
r = urlopen(authorized_keys).read().decode('utf8').split("\n")
for line in r:
    if len(line) != 0:
        authorized_servers.append(str(line))
print('Authorized servers are: \n', authorized_servers)

# Guild joining server
@bot.event
async def on_guild_join(guild):
    users_filepath = f'{cwd}/usrs/users-{guild.id}.txt'
    channels_filepath = f'{cwd}/channels/channel-{guild.id}.txt'

    # Check if server is authorized, if it isn't, check if it's been added since start of the bot.
    if str(guild.id) not in authorized_servers:
        r = urlopen(authorized_keys).read().decode('utf8').split("\n")
        for line in r:
            if len(line) != 0:
                if line not in authorized_servers:
                    authorized_servers.append(str(line))
    # Check if it's then authorized after previous check.
    if str(guild.id) in authorized_servers:
        
        print('Connected to new authorized server!:', guild.name)
        # Create userfile if server hasn't been visited before.
        if not os.path.isfile(users_filepath):
            print(f'User file does not exist, creating for {guild.name}')
            users = {}
            with open(users_filepath, 'w+') as user_file:
                    json.dump(users, user_file)
        else:
            print(f'Userfile for {guild.name} exists')

        # Create channelfile if server hasn't been visited before.
        if not os.path.isfile(channels_filepath):
            print(f'Channel file on {guild.name} file does not exist, creating file for {guild.name}')
            channel = 'general' 
            with open(channels_filepath, 'w+') as channel_file:
                channel_file.write(channel)
        else:
            print(f'Channel file for {guild.name} exists')
        print()
        print()
        print()
    # Leave server if the server is not authorized.
    else:
        print(f'{guild.name} with id {guild.id} is not an authorized server')
        await bot.get_guild(guild.id).leave()

# Bot loading ready status.
@bot.event
async def on_ready():
    
    # Check all servers
    all_guilds = []
    global users
    for g in bot.guilds:
        if g not in all_guilds:
            all_guilds.append(g)
    # Make sure user and channel files exist.
    for guild in all_guilds:
        users_filepath = f'{cwd}/usrs/users-{guild.id}.txt'
        channels_filepath = f'{cwd}/channels/channel-{guild.id}.txt'
    
        if not os.path.isfile(users_filepath):
            print(f'User file does not exist, creating for {guild.name}')
            users = {}
            with open(users_filepath, 'w+') as user_file:
                json.dump(users, user_file)
        else:
            print(f'Userfile for {guild.name} exists')

        if not os.path.isfile(channels_filepath):
            print(f'Channel file on {guild.name} file does not exist, creating file for {guild.name}')
            channel = 'general' 
            with open(channels_filepath, 'w+') as channel_file:
                channel_file.write(channel)
        else:
            print(f'Channel file for {guild.name} exists')

    # Change status to idle and set game status.
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print()
    print()




# Member changing status event
@bot.event  
async def on_member_update(before, after):
    users_filepath = f'{cwd}/usrs/users-{before.guild.id}.txt'
    channels_filepath = f'{cwd}/channels/channel-{before.guild.id}.txt'
    
    # Load all users and channels
    with open(users_filepath, 'r') as user_file:
        users = json.loads(user_file.read())
    
    with open(channels_filepath, 'r') as channel_file:
        channel = channel_file.read().split('\n')[0]
    
    # If the change is made by the bot, ignore
    if str(before.name) == 'StreamStalker':
        pass
    
    # check if the activity change is to start stream
    elif hasattr(after.activity, 'twitch_name') and not hasattr(before.activity, 'twitch_name'):
        guild_id = before.guild.id
        if after.activity.twitch_name in users:
            # Check if user is an authorized streamer from users file for given server.
            try:
                print('Authorized User Found', users[after.activity.twitch_name])
                streamer = after.activity.twitch_name
                curr_user = users[streamer]
                user_list = bot.users

                user_list_str = list(map(str, bot.users))
                
                indes = user_list_str.index(curr_user)
                user_id = user_list[indes].id
                print(user_id)
                member_list = [*bot.get_all_members()]
                # Check if the change is within the actual server and not in any given server.
                for mber in member_list:
                    if mber.id == user_id and mber.guild.id == guild_id:
                        member = mber
                    else:
                        continue
                print(streamer, 'started streaming, go watch at twitch.tv/' + streamer)

                # Assign Twitch Live Role to streaming user
                role = discord.utils.get(after.guild.roles, name="Twitch Live")
                await member.add_roles(role)
                
                # Send message to set channel about user going live
                channel_gen = [*bot.get_all_channels()]
                channel_list = list(map(str, channel_gen))
                channel_index = channel_list.index(channel)
                tar_channel = channel_gen[channel_index]
                await tar_channel.send(f'{member.mention} just started streaming. Go watch them at <https://www.twitch.tv/{streamer}>')

                embed = discord.Embed(title=f"{member.name}'s stream.", description="")
                embed.add_field(name="Titel:", value=f"{after.activity.name}", inline=False)
                embed.add_field(name="Spil:", value=f"{after.activity.details}", inline=False)
                await tar_channel.send(content=None, embed=embed)
            # If user isn't authorized, don't execute.
            except KeyError:
                print('User is not an authorized streamer')
        else:
            print('User is not an authorized streamer')

        

    # Check if transition is from streaming to stopped stream.
    elif hasattr(before.activity, 'twitch_name') and not hasattr(after.activity, 'twitch_name'):
        guild_id = before.guild.id
        # Check if authorized user
        if before.activity.twitch_name in users:
            try:
                streamer = before.activity.twitch_name
                curr_user = users[streamer]
                user_list = bot.users

                user_list_str = list(map(str, bot.users))
                
                indes = user_list_str.index(curr_user)
                user_id = user_list[indes].id
                member_list = [*bot.get_all_members()]
                # Check if change is in current server
                for mber in member_list:
                    if mber.id == user_id and mber.guild.id == guild_id:
                        print('Found member', mber.name)
                        member = mber
                        break
                    else:
                        continue
                # Remove live role from user.
                role = discord.utils.get(before.guild.roles, name="Twitch Live")
                await member.remove_roles(role)

                # Remove live message posted previously for user.
                channel_gen = [*bot.get_all_channels()]
                channel_list = list(map(str, channel_gen))
                channel_index = channel_list.index(channel)
                tar_channel = channel_gen[channel_index]
                flattened =  await tar_channel.history(limit=50).flatten()
                msg_idx = []
                # Look through message history and delete message(s) if it exists
                for message in flattened:
                    if f'{member.mention} har startet sin stream! Se dem på <https://www.twitch.tv/{streamer}>' == message.content:
                        msg_idx.append(flattened.index(message))
                    for embed in message.embeds:
                        if embed.title == f"{member.name}'s stream.":
                            msg_idx.append(flattened.index(message))
                for idx in msg_idx:
                    await flattened[idx].delete()

            except KeyError:
                print('Not authorized Streamer, ignoring')

# Check message sent in set channel
@bot.event
async def on_message(message):
    users_filepath = f'{cwd}/usrs/users-{message.guild.id}.txt'
    channels_filepath = f'{cwd}/channels/channel-{message.guild.id}.txt'

    # Load users and channels
    with open(users_filepath, 'r') as user_file:
        users = json.loads(user_file.read())

    with open(channels_filepath, 'r') as channel_file:
        channels = channel_file.read().split('\n')

    # If the message is created by the bot, ignore.
    if message.author == bot.user:
        return
    # 
    elif str(message.channel) in channels:
        # Check start of messages if they contain sscommands command.
        if message.content.startswith('!addstreamer'):
            print()
            # Check if a mention is used, if so ask user to use discord ID.
            if message.content.split()[2][:2] == "<@":
                await message.channel.send('Please dont use mentions. Remove the # before the discord ID')
            # Add the user to users file. If same username/key is used twice, update value for said key.
            else:
                try:
                    await message.channel.send(f'Adding streamer {message.content.split()[1]}')
                    # Write to user file
                    with open(users_filepath,'w') as user_file:
                        disc_id_list = message.content.split()[2:]
                        disc_id = " ".join(disc_id_list)
                        users[message.content.split()[1]] = disc_id
                        json.dump(users, user_file)
                    print(f'{message.content.split()[1]} added, all users in {message.author.guild} are now {users.items()}')
                    print(f'Keys are {users.keys()}')
                # Check that the amount of arguments are correct.
                except IndexError:
                    await message.channel.send("Remember to type twitch name first and then discord username!")
        # List all authorized streamers/users
        elif message.content.startswith('!streamers'):
            all_streamers = list(users.keys())
            await message.channel.send(f'All streamers connected are:\n{all_streamers}')

        # Display value associated with key
        elif message.content.startswith('!streamer'):
            disc_id_list = message.content.split()[1:]
            disc_id = " ".join(disc_id_list)
            # if authorized user, return key
            try:
                await message.channel.send(f'Discord username connected with {disc_id} is {users[disc_id]}')
            # else don't return anything
            except KeyError:
                await message.channel.send(f'Streamer not authorized')
        # Set which channel the bot should work in.
        elif message.content.startswith('!setchannel'):
            channel_gen = [*bot.get_all_channels()]
            channel_list = list(map(str, channel_gen))
            new_channel_list = message.content.split()[1:]
            # check for spaces in text channel
            new_channel = '\u2009\u2009'.join(map(str, new_channel_list))
            # If channel doesn't exist tell user to check spelling
            if new_channel not in channel_list:
                await message.channel.send(f'{new_channel} does not exist, please make sure the channel name is correct!')
            # Else change to channel provided by user
            else:
                await message.channel.send(f'Working channel set to {new_channel}')
                with open(channels_filepath, 'w') as channel_file:
                    channel_file.write(new_channel)
                print(f'Current channel is {new_channel}')
        # Remove a streamer/user from authorized streamers
        elif message.content.startswith('!removestreamer'):
            # Check argument length
            if len(message.content.split()) > 2:
                await message.channel.send('Remember to only add 1 user, which is the twitch name')
            # Remove streamer/user from list of streamers and export the userfile
            else:
                streamer_of_interest = message.content.split()[1]
                # if streamer/user is authorized remove
                if streamer_of_interest in users:
                    await message.channel.send(f'Removing streamer {streamer_of_interest}')
                    del users[streamer_of_interest]
                    with open(users_filepath,'w') as user_file:
                        json.dump(users, user_file)
                # else let user know the streamer/user doesnt exist
                else:
                    await message.channel.send(f'Streamer {streamer_of_interest} is not an authorized streamer')

        # delete messages
        elif message.content.startswith('!sspurge'):
            msg_len = len(message.content.split())
            if msg_len == 1:
                await message.channel.send('Remember to add the amount of message to be deleted.')
            elif msg_len== 2:
                purged = False
                if purged == False:
                    print('Purging')
                    number_of_messages = int(message.content.split()[1])
                    await message.channel.send(f'Deleting {number_of_messages} messages.')
                    time.sleep(3)
                    await message.channel.purge(limit=number_of_messages+2)
                    purged = True
                    print('Purged', purged)
                        
            else:
                await message.channel.send('Too many arguments, format for command: !command count')

        # List all commands 
        elif message.content.startswith('!sscommands'):
            print('commands has been called')
            embed = discord.Embed(title="Commands for StreamStalker", description="Some useful commands")
            embed.add_field(name="!addstreamer", value="Tilføj streamer til listen over autoriserede streamers - !command twitchname discordid")
            embed.add_field(name="!removestreamer", value="Fjerner en streamer fra listen af autoriserede streamers - !command twitchname")
            embed.add_field(name="!streamers", value="Viser alle autoriserede streamers - !command")
            embed.add_field(name="!streamer", value="Viser det associerede discord ID med nævnte streamer - !command twitchname")
            embed.add_field(name="!setchannel", value="Indstiller den indtastede channel til at være aktuel channel StreamStalker skal virke i - !command channelname")
            embed.add_field(name="!sspurge", value="Deletes selected number of messages from channel - !command messagecount")
            await message.channel.send(content=None, embed=embed)
        
            
bot.run(token)
