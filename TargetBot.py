import discord
import json
import os

#add_bot = 'https://discordapp.com/oauth2/authorize?client_id=701034599970635778&scope=bot&permissions=8'

token = os.environ.get('TB_TOKEN') #client token
help = open('documentation.txt').read() #documentation
servers = json.loads(open('servers.json').read()) #multi-server managment

client = discord.Client()

#multi-server managment
def get_target(server_id):
    try:
        return servers[server_id][0]
    except:
        return ""
        
def get_reply(server_id):
    try:
        return servers[server_id][1]
    except:
        return "no"

def write_map(server_id, target, reply):
    servers.update({server_id: [target ,reply]})
    with open('servers.json', 'w') as f:
        json.dump(servers, f)

@client.event
async def on_message(message):

    server_id = str(message.guild.id)
    target = get_target(server_id)
    reply = get_reply(server_id) 
    is_command = False

    #set target command
    if message.content.startswith("$set_target "):
        is_command = True
        target_name = message.content.replace("$set_target ","")   
        found = False
        #nickname set as target
        user = discord.utils.get(message.guild.members, nick=target_name)
        if user != None:
            found = True
            if user.bot:
                await message.channel.send("you can't target a bot")                
            else:
                target = str(user)
                try:
                    write_map(server_id,target,reply)
                    await message.channel.send(f"{user.mention} is the current target.") 
                except:
                    await message.channel.send(f"There was an unexpected problem")             
        #username set as target
        if not found:
            user = discord.utils.get(message.guild.members, name=target_name)
            if user != None:
                if user.bot:
                    await message.channel.send("you can't target a bot")
                else:
                    target = str(user)
                    try:
                        write_map(server_id,target,reply)   
                        await message.channel.send(f"{user.mention} is the current target.") 
                    except:                       
                        await message.channel.send(f"There was an unexpected problem")
 
            else:
                await message.channel.send(f"{target_name} was not found.")
    
    #set reply command        
    if message.content.startswith("$set_reply "):
        is_command = True
        reply = message.content.replace("$set_reply ","")
        try:
            write_map(server_id,target,reply)
            await message.channel.send("done")
        except:        
            await message.channel.send(f"There was an unexpected problem") 
    
    #help command        
    if message.content.startswith("$help"):
        await message.channel.send(help)
    
    #stop replying command
    if message.content.startswith("$stop"):
        is_command = True
        try:
            write_map(server_id,"",reply)
            await message.channel.send("done")
        except:       
            await message.channel.send(f"There was an unexpected problem") 
    
    #reply to target
    if not is_command and str(message.author) == target:
        await message.channel.send(f"{reply} {message.author.mention}")
     
client.run(token)

