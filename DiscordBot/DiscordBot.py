import discord
import random
import requests
import shutil
import os
from discord import Game
from discord.ext.commands import Bot
import asyncio
import json
import aiohttp
from datetime import datetime
import phonenumbers
import string
import DiscordUtils  # , SMS

# Dictionary of cities where key is the city name and value is a dictionary of metadata like id, country, and coordinates
CITY_DICT = json.load(open('cities.dict.json', encoding='utf-8'))

WEATHER_EMOJI = {'01d': ':sunny:',
                 '01n': ':waxing_gibbous_moon:',
                 '02d': ':white_sun_small_cloud:',
                 '02n': ':cloud:',
                 '03d': ':partly_sunny:',
                 '03n': ':cloud:',
                 '04d': ':white_sun_cloud:',
                 '04n': ':cloud:',
                 '09d': ':cloud_rain:',
                 '09n': ':cloud_rain:',
                 '10d': ':white_sun_rain_cloud:',
                 '10n': ':cloud_rain:',
                 '11d': ':thunder_cloud_rain:',
                 '11n': ':thunder_cloud_rain:',
                 '13d': ':cloud_snow:',
                 '13n': ':cloud_snow:',
                 '50d': ':fog:',
                 '50n': ':fog:'}
WEATHER_API_KEY = '66b9927037479f0f151efdf8ed88aebc'
BOT_PREFIX = ("?", "!")

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    # await client.change_presence(game=Game(name="Raymond's mumbo jumbo", type=2))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command(name='weather',
                description="Tells you the weather of all the cities you enter.\nWon't do anything for cities that aren't in the database.\n\nExamples: !weather Syracuse, !weather New York Boston ",
                brief="Weather for the locations you enter",
                aliases=['temperature', 'temp', 'forecast'],
                pass_context=True)
async def weather(context):
    # exclude the command itself
    city_list = context.message.content.title().split()[1:]
    # checks to see if city list is empty
    if not city_list:
        await context.channel.send(" You didn't provide a city name, " + context.message.author.mention)
    else:
        confirmed_cities = DiscordUtils.check_valid_city(city_list, CITY_DICT)
        # calls api using the city names
        for city in confirmed_cities:
            try:
                city_id = CITY_DICT[city]['id']
                url = 'http://api.openweathermap.org/data/2.5/weather?id=' + \
                    str(city_id) + '&mode=json&units=imperial&APPID=' + \
                    WEATHER_API_KEY
                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(url)
                    data = await raw_response.json()
                    report = 'Current weather as of '
                    report += datetime.fromtimestamp(data['dt']).strftime(
                        "%A, %B %d, %Y %I:%M%p") + ' for ' + data['name'] + ', ' + data['sys']['country'] + '\n'
                    report += '---------------------------------------------------------------------------------\n'
                    report += 'Temperature: %.1fF\n' % data['main']['temp']
                    report += 'Description: %s %s\n' % (
                        WEATHER_EMOJI[data['weather'][0]['icon']], data['weather'][0]['description'].title())
                    report += 'Pressure: %d hPA\n' % data['main']['pressure']
                    report += 'Humidity: %d%%\n\n' % data['main']['humidity']
                    await context.channel.send(report)
            except KeyError:
                await context.channel.send(("Something went wrong when retrieving data for %s, " + context.message.author.mention) % city)


@client.command(name='8ball',
                description="Answers a yes/no question.",
                brief="Answers from the beyond.",
                aliases=['eight_ball', 'eightball', '8-ball'],
                pass_context=True)
async def eight_ball(context):
    possible_responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'Definitely',
    ]
    if len(context.message.content.split()) == 1:
        await context.channel.send("You didn't ask a question for the prophet to answer, " + context.message.author.mention)
    else:
        await context.channel.send(random.choice(possible_responses) + ", " + context.message.author.mention)


@client.command(name='late',
                description="Submits my late pass",
                brief="late pass",
                pass_context=True)
async def late(context):
    file_path = "images/"+str(context.author.id)+".png"
    if os.path.isfile(file_path):
        await context.channel.send('{name}\'s late pass'.format(name=context.author.display_name), file=discord.File(file_path))
    else:
        await context.channel.send("Your late pass isn't registered")
    
@client.command(name='register',
                description="Registers something, like late pass(i.e !register late pass)",
                brief="Register something",
                pass_context=True)
async def register(context):
    task = context.message.content.lower().split()[1:]
    try:
        if "late" in task and "pass" in task:
            await late_pass_registration(context)
        elif "movie" in task and "name" in task:
            await movie_name_registration(context, task)
        else:
            await context.channel.send("Could not match item to register")
    except Exception as e:
        print(e)
        await context.channel.send("Something went wrong, could not complete registration")

async def late_pass_registration(context):
    if context.message.attachments:
        url = context.message.attachments[0].url
        if url[0:26] == "https://cdn.discordapp.com":
            r = requests.get(url, stream=True)
            with open(("images/"+str(context.author.id)+".png"), 'wb+') as out_file:
                shutil.copyfileobj(r.raw, out_file)
                await context.channel.send("Your late pass has been registered")

async def movie_name_registration(context, args):
    args.remove("movie")
    args.remove("name")
    if args:
        nameList = json.load(open('movieNames.json'))
        viewerName = ' '.join(args)
        with open('movieNames.json', 'w+') as fp:
            nameList[viewerName] = context.author.id
            json.dump(nameList, fp)
            await context.channel.send("Your movie name has been registered")
    else:
        await context.channel.send("No name has been entered")

# @client.command(name='num_messages',
#                description="Tells you how many messages you've posted in this channel maxed at 100",
#                brief="# of messages in channel",
#                pass_context=True)
# async def num_messages(context):
#     counter = 0
#     tmp = await context.channel.send('Calculating messages...')
#     async for log in client.logs_from(context.message.channel, limit=100):
#         if log.author == context.message.author:
#             counter += 1
#     await client.edit_message(tmp, 'You have {} messages.'.format(counter))


# @client.command(name="text_alert",
# 				description="Sends an SMS to a person if they're offline.\n" +
# 							"Register your phone number and provider using '!text_alert new [provider] ###-###-####'\n" +
# 							"Turn text alert on using '!text_alert on'\n" +
# 							"Turn text alert off using '!text_alert off'\n" +
# 							"\nRegistering example: !text_alert new T-Mobile 123-456-7890" +
# 							"*Note: Turning text alert on or off assumes you have a number registered.\n" +
# 							"\nList of providers: \n['att', 'tmobile', 'verizon', 'sprint', 'virginmobile', 'tracfone', 'metropcs', 'boostmobile', 'cricket','republicwireless', 'googlefi', 'uscellular', 'ting', 'consumercellular', 'cspire', 'pageplus', 'other']",
# 				brief="Sends an SMS to a person if they're offline",
# 				aliases=['text', 'message_me', 'SMS'],
# 				pass_context=True)
# async def text_alert(context):
# 	argument = context.message.content.lower().split()[1:]
# 	if argument == []:
# 		await client.say("Sorry, those parameters don't do anything. Please consult !help for command help, " + context.message.author.mention)
# 	elif argument[0] == 'new':
# 		try:
# 			number = '+1' + (''.join(argument[2:]))
# 			number = phonenumbers.parse(number, None)
# 			providers_list = ['att', 'tmobile', 'verizon', 'sprint', 'virginmobile', 'tracfone', 'metropcs', 'boostmobile', 'cricket','republicwireless', 'googlefi', 'uscellular', 'ting', 'consumercellular', 'cspire', 'pageplus', 'other']
# 			myprovider = ''.join(c for c in argument[1] if c not in string.punctuation).lower()
# 			if myprovider not in providers_list:
# 				raise ValueError
# 			if phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number):
# 				profile_info = json.load(open('text_alert.json'))
# 				profile_info[context.message.author.display_name + '#' + context.message.author.discriminator] = {'provider': argument[1], 'number':number.national_number, 'alert': True}
# 				with open('text_alert.json', 'w') as fp:
# 					json.dump(profile_info, fp)
# 				await client.say("Phone Number sucessfully added, " + context.message.author.mention)
# 		except (phonenumbers.NumberParseException, IndexError, ValueError) as e:
# 			await client.say("Sorry boss, that's not a valid phone number or service provider, " + context.message.author.mention)
# 	elif argument[0] == 'on':
# 		try:
# 			profile_info = json.load(open('text_alert.json'))
# 			profile_info[context.message.author.display_name + '#' + context.message.author.discriminator]['alert'] = True
# 			with open('text_alert.json', 'w') as fp:
# 					json.dump(profile_info, fp)
# 			await client.say("Alerts turned on, " + context.message.author.mention)
# 		except KeyError:
# 			await client.say("You haven't registered a phone number yet, " + context.message.author.mention)
# 	elif argument[0] == 'off':
# 		try:
# 			profile_info = json.load(open('text_alert.json'))
# 			profile_info[context.message.author.display_name + '#' + context.message.author.discriminator]['alert'] = False
# 			with open('text_alert.json', 'w') as fp:
# 					json.dump(profile_info, fp)
# 			await client.say("Alerts turned off, " + context.message.author.mention)

# 		except KeyError:
# 			await client.say("You haven't registered a phone number yet, " + context.message.author.mention)
# 	else:
# 		await client.say("Sorry, those parameters don't do anything. Please consult !help for command help, " + context.message.author.mention)


@client.event
async def on_message(message):
    if not message.author.bot:
        # Checks if any commands match it before doing anything else
        await client.process_commands(message)

        #	await client.edit_message(tmp, 'You have {} messages.'.format(counter))
        if message.content.startswith('!sleep'):
            await asyncio.sleep(5)
            await message.channel.send('Done sleeping')

        # for user in message.mentions:
        # 	if user.status == discord.Status.offline:
        # 		number, provider = DiscordUtils.get_user_contacts(user)
        # 		if provider == 'other':
        # 			SMS.send_via_twilio(message, number)
        # 			await client.send_message(message.channel, ("SMS message was sent to " + user.display_name))
        # 		else:
        # 			handle = SMS.Gmail()
        # 			sender = "mygmail@gmail.com"
        # 			to = str(number) + provider
        # 			subject = message.author.name
        # 			message_text = message.clean_content
        # 			message_package = SMS.CreateMessage(sender, to, subject, message_text)
        # 			handle = handle.SendMessage("me", message_package)
        # 			await client.send_message(message.channel, ("SMS message was sent to " + user.display_name))

    # Movie List Webhook
    #748306659423813722 webhook id for test server
    elif message.author.id == 749034575107457055:
        moviePings = json.loads(message.content)
        movieMessage = '**' + moviePings['movieName'] + '** in ' + str(moviePings['timeUntil']) + ' minutes, '
        with open('movieNames.json', 'r') as fp:
            viewerIDs = json.loads(fp.read())
            for viewer in moviePings['allViewers']:
                viewer = viewer.lower().strip()
                if viewerIDs.get(viewer):
                    movieMessage += "<@" + str(viewerIDs[viewer]) + "> "
        await message.delete()
        await message.channel.send(movieMessage)

client.run('NDIzNzY3Nzc1MzA4MTUyODMy.DbZ8kQ.beeBUKbXbdbZCMVxXrHux1ZCWYo') # prod bot
#client.run('NzQ4MjgzNDczMDA5MzExODU0.X0bLSg.oPvZddp24YRJZlH12sJx4Kx0jXE') #dev bot