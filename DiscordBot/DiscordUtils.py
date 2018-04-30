import json

PROVIDER_MAP = {'att' : '@txt.att.net',
				'attmms' : '@mms.att.net',
				'tmobile' : '@tmomail.net',
				'tmobilemms' : '@tmomail.net',
				'verizon' : '@vtext.com',
				'verizonmms' : '@vzwpix.com',
				'sprint' : '@messaging.sprintpcs.com',
				'sprintmms' : '@pm.sprint.com',
				'virginmobile' : '@vmobl.com',
				'virginmobilemms' : '@vmpix.com',
				'tracfone' : '@mmst5.tracfone.com',
				'metropcs' : '@mymetropcs.com',
				'metropcsmms' : '@mymetropcs.com',
				'boostmobile' : '@sms.myboostmobile.com',
				'boostmobile' : '@myboostmobile.com ',
				'cricket' : '@sms.cricketwireless.net',
				'cricketmms' : '@mms.cricketwireless.net',
				'republicwireless' : '@text.republicwireless.com',
				'googlefi' : '@msg.fi.google.com',
				'googlefimms' : '@msg.fi.google.com',
				'uscellular' : '@email.uscc.net',
				'uscellularmms' : '@mms.uscc.net',
				'ting' : '@message.ting.com',
				'consumercellular' : '@mailmymobile.net',
				'cspire' : '@cspire1.com',
				'pageplus' : '@vtext.com'
				}

def check_valid_city(str_list, CITY_DICT):
	''' 
	Gets a list of strings and checks if those strings are either multiworded cities or single worded cities. Returns a list of strings of valid cities	
	'''
	all_cities = list(CITY_DICT.keys())
	#compares each word and it's consecutive word/s joined together to see if it's a city (ie. New York, Salt Lake City)
	confirmed_cities = []
	index = 0
	while index < len(str_list):
		if (str_list[index] + ' ' + str_list[(index+1)%len(str_list)] + ' ' + str_list[(index+2)%len(str_list)]) in all_cities:
			confirmed_cities.append((str_list[index] + ' ' + str_list[(index+1)%len(str_list)] + ' ' + str_list[(index+2)%len(str_list)]))
			#skip 2 indexes if we use the next two consecutive words
			index += 2
		elif (str_list[index] + ' ' + str_list[(index+1)%len(str_list)]) in all_cities:
			confirmed_cities.append((str_list[index] + ' ' + str_list[(index+1)%len(str_list)]))
			#skip an index if we use the next consecutive word
			index += 1
		elif str_list[index] in all_cities:
			confirmed_cities.append(str_list[index])
		#regardless of what we do anything above, we move on to next index
		index += 1
	return confirmed_cities

def get_user_contacts(user):
	profile_info = json.load(open('text_alert.json'))
	name = user.display_name + '#' + user.discriminator
	if name in profile_info.keys():
		if profile_info[name]['alert']:
			number = profile_info[name]['number']
			try:
				provider = PROVIDER_MAP[profile_info[name]['provider']]
			except KeyError:
				provider = 'other'
	return number, provider