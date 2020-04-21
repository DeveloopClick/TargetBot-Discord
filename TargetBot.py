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

def get_pre(server_id):
    try:
        return servers[server_id][2]
    except:
        return '$'

def get_permitted(server_id):
    try:
        return servers[server_id][3]
    except:
        return []

def reset_server(server_id):
    servers.update({server_id: ["", "no", '$', []]})
    with open('servers.json', 'w') as f:
        json.dump(servers, f)


def write_server(server_id, target, reply, pre, command, permitted):
    if command == None:
        servers.update({server_id: [target, reply, pre, permitted]})
    elif command == 'add':
        all_permitted = get_permitted(server_id)
        all_permitted.extend(permitted)
        servers.update({server_id: [target, reply, pre, all_permitted]})
    elif command == 'remove':
        all_permitted = get_permitted(server_id)
        servers.update({server_id: [target, reply, pre, [x for x in all_permitted if x not in permitted]]})
    else:
        raise NameError
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
    pre = get_pre(server_id)
    permitted = get_permitted(server_id)
 
    #set permissions
    if message_content.startswith(pre + "edit_permissions"):
        is_command = True
        if message.author.permissions_in(message.channel).administrator:
            edit = discord.Embed(title="Edit Permissions",description="decide which roles can use the bot")
            edit.add_field(name="**the current roles that can use the bot, except Administrator, are:**", value=f"**{[message.guild.get_role(x).mention for x in permitted]}**")
            edit.add_field(name="**to add roles:**", value="`add <role>:`", inline=False)
            edit.add_field(name="**to remove roles:**", value="`remove <role>:`", inline=False)
            await message.channel.send(content=None, embed=edit)
            def command(message):
                return (message.content.startswith('add') or message.content.startswith('remove')) 
            try:
                message = await client.wait_for('message', check=command, timeout=30.0)
            except asyncio.TimeoutError:
                await message.channel.send("timeout, try again.")
            else:
                if message.content.startswith('add'):
                    command = 'add'
                    added = []
                    added_mention = ""
                    for role in message.role_mentions:
                        if role not in [message.guild.get_role(x) for x in permitted]:
                            added.append(role.id)
                        else: 
                                await message.channel.send(f"{role.mention} role is already permitted to use the robot")
                    if added:
                        for role in added:
                            added_mention += f"{message.guild.get_role(role).mention} "
                        await message.channel.send(f'this will add {added_mention}\n are you sure? reply \'yes\' if so.')

                        def check(message):
                            return (message.content == 'yes' or message.content == '\'yes\'')

                        try:
                            message = await client.wait_for('message', check=check, timeout=15.0)
                        except asyncio.TimeoutError:
                            await message.channel.send("addition canceled.")
                        else:
                            try:
                                write_server(server_id, target, reply, pre, 'add', added)
                            except:
                                await message.channel.send("there was a problem; addition canceled.")
                            else:
                                await message.channel.send(f"{added_mention}'s role users are now as well able to use the bot.")
                    else:
                        await message.channel.send("no one to add, try again.")

                elif message.content.startswith('remove'):
                    command = 'remove'
                    removed = []
                    removed_mention = ""
                    for role in message.role_mentions:
                        if role in [message.guild.get_role(x) for x in permitted]:
                            removed.append(role.id)
                        else: 
                                await message.channel.send(f"{role.mention} role is not a premitted role.")
                    if removed:
                        for role in removed:
                            removed_mention += f"{message.guild.get_role(role).mention} "
                        await message.channel.send(f'this will remove {removed_mention}\n are you sure? reply \'yes\' if so.')

                        def check(message):
                            return (message.content == 'yes' or message.content == '\'yes\'')

                        try:
                            message = await client.wait_for('message', check=check, timeout=15.0)
                        except asyncio.TimeoutError:
                            await message.channel.send("removal canceled.")
                        else:
                            try:
                                write_server(server_id, target, reply, pre, 'remove', removed)
                            except:
                                await message.channel.send("there was a problem; removal canceled.")
                            else:
                                await message.channel.send(f"{removed_mention}'s users are not longer able to use the bot.")
                    else:
                        await message.channel.send("no one to remove, try again.")
        else:
            await message.channel.send("only administrators are allowed to edit permissions.")

    #set target command
    elif message_content.startswith(pre + "target "):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            target_name = message.content[8::]  
            user = discord.utils.get(message.guild.members, nick=target_name) #user as nick
            if user == None:
                user = discord.utils.get(message.guild.members, name=target_name) #user as name
            if user == None:
                try: #user as mantioned
                    user = message.mentions[0] 
                except:
                    pass
            if user != None:
                if user.bot:
                    await message.channel.send("you can't target a bot")
                else:
                    target = str(user)
                    try:
                        write_server(server_id, target, reply, pre, None, permitted)   
                    except:                       
                        await message.channel.send(f"there was an unexpected problem")
                    else:
                        await message.channel.send(f"{user.mention} is the current target.") 
            else:
                await message.channel.send(f"{target_name} was not found.")
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")
    
    #bomb message command
    elif message_content.startswith(pre + "bomb "):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            bombed = discord.utils.get(message.guild.members, name=target.translate({ord(i): None for i in '#1234567890'}))
            times = int(message_content.replace(pre + "bomb ",""))
            if times in range(1,11):
                for i in range(1,times+1):
                    try:
                        await message.channel.send(f"{i}. {reply} {bombed.mention} :)")
                    except:
                        await message.channel.send(f"{i}. {reply}")
            else:
                await message.channel.send("there's a maximum of 10 bomb-messages; try again.")
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")

    #set reply command        
    elif message_content.startswith(pre + "set_reply "):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            reply = message.content[11::]
            try:
                write_server(server_id, target, reply, pre, None, permitted)            
            except:        
                await message.channel.send(f"There was an unexpected problem") 
            else:   
                await message.channel.send("done")
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")
    
    #stop replying command
    elif message_content.startswith(pre + "stop"):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            try:
                write_server(server_id, "", reply, pre, None, permitted)
                await message.channel.send("done")
            except:       
                await message.channel.send(f"There was an unexpected problem") 
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")

    #set prefix command
    elif message_content.startswith(pre + "set_prefix "):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            pre = message.content[13::]
            try:
                write_server(server_id, target, reply, pre, None , permitted)
                await message.channel.send("done")
            except:       
                await message.channel.send(f"There was an unexpected problem") 
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")
    
    #reset server
    elif message_content.startswith(pre + "reset") or message_content.startswith("$reset"):
        #check if user is permitted to use the bot
        if [x for x in message.author.roles if x.id in permitted] or message.author.permissions_in(message.channel).administrator:
            is_command = True
            await message.channel.send('this will reset the target, reply and prefix.\n are you sure? reply \'yes\' if so.')

            def confirmation(message):
                return (message.content == 'yes' or message.content == '\'yes\'')

            try:
                message = await client.wait_for('message', check=confirmation, timeout=15.0)
            except asyncio.TimeoutError:
                await message.channel.send("reset canceled.")
            else:
                try:
                    reset_server(server_id)
                except:
                    await message.channel.send("there was a problem; reset canceled.")
                else:
                    await message.channel.send("the bot has been reset successfully.")
        else:
            await message.channel.send("you can't use the bot, ask one of the Admins to add your role as permitted.")
        
    #help command - documentation       
    elif message_content.startswith(pre + "help") or message_content.startswith("$help"):
        is_command = True
        help = discord.Embed(title="Help For TargetBot",description="List of useful commands: \n`(defaults: target - None; reply - \"no\"; bot prefix - \'$\')`")
        help.add_field(name=f"**{pre}target <user>**", value="target the user.")
        help.add_field(name=f"**{pre}set_reply <string>**", value="set a new reply for the target.")     
        help.add_field(name=f"**{pre}bomb <n>**", value="bomb-reply to target n times.") 
        help.add_field(name=f"**{pre}stop**", value="stop replying to target by removing the current target.") 
        help.add_field(name=f"**{pre}set_prefix <char>**", value="set new prefix for the bot.") 
        if message.author.permissions_in(message.channel).administrator:
            help.add_field(name=f"**{pre}edit_permissions**", value="decide which roles can use the bot, follow the instructions.") 
        if pre != '$':
            help.add_field(name=f"**{pre}help** / $help", value="show list of commands.") 
            help.add_field(name=f"**{pre}reset** / $reset", value="reset all to default: target, reply, prefix.") 
        else:
            help.add_field(name=f"**{pre}help**", value="show list of commands.") 
            help.add_field(name=f"**{pre}reset**", value="reset all to default: target, reply, prefix.") 
        await message.channel.send(content=None, embed=help)

    #reply to target
    if not is_command and str(message.author) == target:
        await message.channel.send(f"{reply} {message.author.mention}")
     
client.run(token)

