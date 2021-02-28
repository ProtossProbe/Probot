import os
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
HELP_MESSAGE = os.getenv('HELP_MESSAGE').replace(r'\n', '\n')
WRONG_MESSAGE = os.getenv('WRONG_MESSAGE').replace(r'\n', '\n')
NOUSER_MESSAGE = os.getenv('NOUSER_MESSAGE').replace(r'\n', '\n')
NOSELF_MESSAGE = os.getenv('NOSELF_MESSAGE').replace(r'\n', '\n')
REPEAT_MESSAGE = os.getenv('REPEAT_MESSAGE').replace(r'\n', '\n')
CLEAR_MESSAGE = os.getenv('CLEAR_MESSAGE').replace(r'\n', '\n')
YOURCRUSH_MESSAGE = os.getenv('YOURCRUSH_MESSAGE').replace(r'\n', '\n')
CRUSHEET_MESSAGE = os.getenv('CRUSHEET_MESSAGE').replace(r'\n', '\n')
NEWS_MESSAGE = os.getenv('NEWS_MESSAGE').replace(r'\n', '\n')
SUCCESS_MESSAGE = os.getenv('SUCCESS_MESSAGE').replace(r'\n', '\n')
SERVER_ID = int(os.getenv('SERVER_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))


def read_crusheet():
    with open('crusheet.json') as f:
        data = json.load(f)
    return data

def save_crusheet(data):
    with open('crusheet.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("DATA SAVED!")

def search_user(data, author):
    idx = 0
    for user in data['user']:
        if (author.id == user['id']):
            return idx
        idx += 1
    return -1

async def print_yourcrush(user):
    crush_list = user['crush']
    info = YOURCRUSH_MESSAGE.format(len(crush_list))
    for crush_id in crush_list:
        crush = await client.fetch_user(crush_id)
        print(crush)
        info += crush.name + '\n'
    return info

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        print("Help!")
        await message.channel.send(HELP_MESSAGE)   

    if isinstance(message.channel, discord.channel.DMChannel):

        # Read the datasheet and search for the sender
        data = read_crusheet()
        user_idx = search_user(data, message.author)

        # If the user is a new user
        if(user_idx == -1):
            print("New User!")
            await message.author.send(HELP_MESSAGE)
            data['user'].append({'id': message.author.id, 'crush': [], 'isMulti': False})

        # If the user is an existant user
        else:
            if message.content.startswith('$crush'): 
                msg = message.content.split()
                if(len(msg) == 2 or len(msg) == 3):       
                    try:
                        crush_id = int(msg[1])
                        await client.fetch_user(crush_id)

                        if(crush_id == message.author.id):
                            await message.author.send(NOSELF_MESSAGE)
                        elif(crush_id in data['user'][user_idx]['crush']):
                            await message.author.send(REPEAT_MESSAGE)
                        else:
                            print("Setting...")
                            if(len(msg) == 3):
                                if(msg[2] == '是'):
                                    data['user'][user_idx]['isMulti'] = True
                                elif(msg[2] == '否'):
                                    data['user'][user_idx]['isMulti'] = False
                                else:
                                    await message.author.send(WRONG_MESSAGE)

                            if(data['user'][user_idx]['isMulti']):
                                data['user'][user_idx]['crush'].append(crush_id)
                            else:
                                data['user'][user_idx]['crush'] = []
                                data['user'][user_idx]['crush'].append(crush_id)
                            await message.author.send(SUCCESS_MESSAGE)
                            info = await print_yourcrush(data['user'][user_idx])
                            await message.author.send(info)

                            for user in data['user']:
                                if(crush_id == user['id'] and message.author.id in user['crush']):
                                    channel = client.get_channel(CHANNEL_ID)
                                    await channel.send(NEWS_MESSAGE.format(message.author.id, crush_id))

                    except:
                        await message.author.send(NOUSER_MESSAGE)

            if message.content.startswith('$list'):
                print("Look Up!")
                info = await print_yourcrush(data['user'][user_idx])
                await message.author.send(info)
            if message.content.startswith('$clear'):
                print("Clear!")
                data['user'][user_idx]['crush'] = []
                await message.author.send(CLEAR_MESSAGE)
        save_crusheet(data)

    if message.content.startswith('$stats'):
        print("Print Crusheet to Lobby")
        data = read_crusheet()
        users = data['user']
        user_count = len(users)
        crush_count = 0
        for user in users:
            crush_count += len(user['crush'])
        await message.channel.send(CRUSHEET_MESSAGE.format(user_count, crush_count))

client.run(os.getenv('TOKEN'))