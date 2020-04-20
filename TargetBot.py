import discord
import json
import asyncio

#TODO:  permissions, hide, delete, logs  
#add_bot = 'https://discordapp.com/oauth2/authorize?client_id=701034599970635778&scope=bot&permissions=8'

token = open('token.txt').read() #client token
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

def get_init(server_id):
    try:
        return servers[server_id][2]
    except:
        return '$'

def reset_server(server_id):
    servers.update({server_id: ["", "no", '$']})
    with open('servers.json', 'w') as f:
        json.dump(servers, f)

def write_server(server_id, target, reply, init):
    servers.update({server_id: [target, reply, init]})
    with open('servers.json', 'w') as f:
        json.dump(servers, f)

@client.event
async def on_message(message):

    message_content = message.content.lower()
    is_command = False
    #get variables
    server_id = str(message.guild.id) 
    target = get_target(server_id)
    reply = get_reply(server_id) 
    init = get_init(server_id)

    #set target command
    if message_content.startswith(init + "set_target "):
        is_command = True
        target_name = message.content[12::]  
        print(target_name)
        user = discord.utils.get(message.guild.members, nick=target_name)
        if user == None:
             user = discord.utils.get(message.guild.members, name=target_name)
        if user != None:
            if user.bot:
                await message.channel.send("you can't target a bot")
            else:
                target = str(user)
                try:
                    write_server(server_id, target, reply, init)   
                except:                       
                    await message.channel.send(f"there was an unexpected problem")
                else:
                    await message.channel.send(f"{user.mention} is the current target.") 
        else:
            await message.channel.send(f"{target_name} was not found.")
    
    #bomb message command
    if message_content.startswith(init + "bomb "):
        is_command = True
        bombed = discord.utils.get(message.guild.members, name=target.translate({ord(i): None for i in '#1234567890'}))
        times = int(message_content.replace(init + "bomb ",""))
        if times in range(1,11):
            for i in range(1,times+1):
                try:
                    await message.channel.send(f"{i}. {reply} {bombed.mention} :)")
                except:
                    await message.channel.send(f"{i}. {reply}")
        else:
             await message.channel.send("there's a maximum of 10 bomb-messages; try again.")

    #set reply command        
    if message_content.startswith(init + "set_reply "):
        is_command = True
        reply = message.content[11::]
        try:
            write_server(server_id, target, reply, init)            
        except:        
            await message.channel.send(f"There was an unexpected problem") 
        else:   
            await message.channel.send("done")
    
    #help command - documentation       
    if message_content.startswith(init + "help") or message_content.startswith("$help"):
        is_command = True
        help = discord.Embed(title="Help For TargetBot",description="List of useful commands: \n`(defaults: target - None; reply - \"no\"; bot initial - \'$\')`")
        help.add_field(name=f"**{init}set_target <user>**", value="set user as target.")
        help.add_field(name=f"**{init}set_reply <string>**", value="set a new reply for the target.")     
        help.add_field(name=f"**{init}bomb <n>**", value="bomb-reply to target n times.") 
        help.add_field(name=f"**{init}stop**", value="stop replying to target; remove the target.") 
        help.add_field(name=f"**{init}set_initial <char>**", value="set new initial for the bot.") 
        if init != '$':
            help.add_field(name=f"**{init}reset** / $reset", value="reset all to default: target, reply, initial.") 
            help.add_field(name=f"**{init}help** / $help", value="show list of commands.") 
        else:
            help.add_field(name=f"**{init}reset**", value="reset all to default: target, reply, initial.") 
            help.add_field(name=f"**{init}help**", value="show list of commands.") 
        await message.channel.send(content=None, embed=help)
    
    #stop replying command
    if message_content.startswith(init + "stop"):
        is_command = True
        try:
            write_server(server_id, "", reply, init)
            await message.channel.send("done")
        except:       
            await message.channel.send(f"There was an unexpected problem") 
    
    #set initial command
    if message_content.startswith(init + "set_initial "):
        is_command = True
        init = message.content[13::]
        try:
            write_server(server_id, target, reply, init)
            await message.channel.send("done")
        except:       
            await message.channel.send(f"There was an unexpected problem") 
    
    #reset server
    if message_content.startswith(init + "reset") or message_content.startswith("$reset"):
        is_command = True
        await message.channel.send('this will reset the target, reply and initial.\n are you sure? reply \'yes\' if so.')

        def check(message):
            return (message.content == 'yes' or message.content == '\'yes\'')

        try:
            message = await client.wait_for('message', check=check, timeout=15.0)
        except asyncio.TimeoutError:
            await message.channel.send("reset canceled.")
        else:
            try:
                reset_server(server_id)
            except:
                await message.channel.send("there was a problem; reset canceled.")
            else:
                await message.channel.send("the bot has been reset successfully.")

    #reply to target
    if not is_command and str(message.author) == target:
        await message.channel.send(f"{reply} {message.author.mention}")
     
client.run(token)

