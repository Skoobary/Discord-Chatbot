from discord.ext import commands
from prsaw import RandomStuff #AI
import time #Timer/Time                              #Import Libraries/Modules
import random #To randomize
import discord #Discord API to make the bot
from pymongo import MongoClient # NoSql Database

############################  Copyright Poseidon Studios ############################
#VARIABLES
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="<", intents=intents) # Set prefix(<) and intents(all)
rs = RandomStuff(async_mode=True)
client.remove_command('help') 


# Connect to DATABASE
cluster = MongoClient("mongodb+srv://JohnUser:<PASSWORD>@johncluster.xsyrt.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["discord"]#mine is serverinfo but you can choose how to call it in yout database
serverInfo = db["serverInfo"]#mine is serverinfo but you can choose how to call it in yout database

############################  Copyright Poseidon Studios ############################

@client.event
async def on_command_error(ctx, error): #error handling
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(description = ctx.author.name + " doesn't have admin permissions ;-;")
        await ctx.send(embed=embed) #Send embed message

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(description = "Please enter all the required arguments.")
        await ctx.send(embed=embed)
        await ctx.message.delete()
    
    elif isinstance(error, commands.CommandOnCooldown):
        with open('still_on_cooldown.gif', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
        

@client.event
async def on_ready(): #When bot connected
  print("Logged as {0.user}".format(client))

@client.event
async def on_guild_join(guild): #Once bot gets invited (server is passed)
	guild_id = guild.id
	guild_name = guild.name
	post_server_info = {
		"guild_name": guild_name,    #Post dictionnary variable
		"guild_id": guild_id, 
		"talk_channels": [], 
        "is_enabled": True,
		}
	serverInfo.insert_one(post_server_info) #Inserts post in database
	print(str(guild_name) + " : " + str(guild_id)) #Prints out guild name + id

@client.command(pass_contect = True)
async def help(ctx):
    embed=discord.Embed(title="Support Us !", url="https://top.gg/bot/834790647889657926", description="Bombaka is an AI-based discord chatting bot. Bombaka has a sister, Mouchibo, you can even add her and make them talk together ! In order to use the bot, use the prefix \"***<***\" followed by the command.", color=0xe7f672)
    embed.set_author(name="Need some help ?")
    embed.set_thumbnail(url='https://stickershop.line-scdn.net/stickershop/v1/product/4863808/LINEStorePC/main.png;compress=true')
    embed.add_field(name="- To setup bot's response channels  (Admin permissions have to be acquired before setting up the channels)", value="setChannels #example1 #ex2", inline=False)
    embed.add_field(name="- Enable Bot's AI function", value="enable", inline=True)
    embed.add_field(name="- Disable Bot's AI function", value="disable", inline=True)
    embed.add_field(name="- Report an issue to dev. team", value="report My issue is...", inline=False)
    embed.set_footer(text="Developped and designed by Poseidon Studios")
    await ctx.send(embed=embed)
    print("Help command used ! : " + ctx.guild.name + "    : " + ctx.author.name)
    return


@commands.cooldown(1, 43200, commands.BucketType.user)
@client.command(pass_context = True)    
async def report(ctx, *, issue):
    f = open("reports.txt", "a")
    f.write("\n______ ____________________")
    f.write("\nIssue : " + str(issue) + " : " + str(ctx.author.name) + "#" + str(ctx.author.discriminator) + " : " + str(ctx.guild.id))
    f.close()
    with open('succes_reported.gif', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
    print("Issue Reported !")

@client.command(pass_context = True)    
async def setChannels(ctx):
    if not len(ctx.message.channel_mentions):
        await ctx.send("Please enter all the required arguments.")
        await ctx.message.delete()
    elif ctx.message.author.guild_permissions.administrator: #Check if message author has admin perms
        talk_channels = []
        for channel in ctx.message.channel_mentions:
            talk_channels.append(channel.id)
        serverInfo.update_one({"guild_id":ctx.guild.id}, {"$set":{"talk_channels": talk_channels}}) #updates "talk_channels" var in database
        with open('success_setup.gif', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
        print("Channel successfuly setup : " + ctx.guild.name + ": \n" + str(talk_channels))

@client.command(pass_context = True)        
async def enable(ctx):
    if ctx.message.author.guild_permissions.administrator: #Check if message author has admin perms
        serverInfo.update_one({"guild_id":ctx.guild.id}, {"$set":{"is_enabled": True}}) #updates "talk_channels" var in database
        embed = discord.Embed(description = "Bombaka is now enabled and will respond to any requests/messages. \n (Channels must be setup) ")
        await ctx.reply(embed=embed) #Send embed message
        print("Bot AI function's enabled : " + ctx.guild.name)

@client.command(pass_context = True)    
async def disable(ctx):
    if ctx.message.author.guild_permissions.administrator: #Check if message author has admin perms
        serverInfo.update_one({"guild_id":ctx.guild.id}, {"$set":{"is_enabled": False}}) #updates "talk_channels" var in database
        embed = discord.Embed(description = "Bombaka is now disabled and will no longer respond to any requests/messages.")
        await ctx.reply(embed=embed) #Send embed message
        print("Bot AI function's disabled : " + ctx.guild.name)


@client.event
async def on_message(message):
    if message.author == client.user: #Returns nothing if message was sent by client (bot)
        return

    results = serverInfo.find({"guild_id" : message.guild.id})      
    for result in results:                      #Gets is_enabled variable from MongoDB noSQL database
        is_enabled = result["is_enabled"]

    ###################################################
    if is_enabled == True:
        await do_ai_stuff(message)

    await client.process_commands(message) #Process Commands

async def do_ai_stuff(message):
    results = serverInfo.find({"guild_id" : message.guild.id})      
    for result in results:
        talking_channels = result["talk_channels"]

    if message.channel.id in talking_channels: #Check if channel where message was sent in database variable
        response = await rs.get_ai_response(message.content) #Get AI response
 #Wait between 4 and 9 seconds
        await message.reply(response) #Reply the AI response
    
############################  Copyright @Poseidon_Studios ############################


client.run("TOKEN") #Run Bot
