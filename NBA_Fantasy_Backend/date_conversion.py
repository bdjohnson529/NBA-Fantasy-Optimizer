def convert_date(abbreviated_date):
	date_split = abbreviated_date.split("-")

	newdatestr = ""

	month = int(date_split[1])

	if(month == 1):
		newdatestr += "Jan "
	elif(month == 2):
		newdatestr += "Feb "
	elif(month == 3):
		newdatestr += "Mar "
	elif(month == 4):
		newdatestr += "Apr "
	elif(month == 5):
		newdatestr += "May "

	day = date_split[2]
	newdatestr += day
	newdatestr += ", "

	year = date_split[0]
	newdatestr += year

	return newdatestr

def convert_date_url(date_url):
	year = date_url[:4]
	month = date_url[4:6]
	day = date_url[6:]

	print year, month, day

def create_date_url(todays_date):
	date_split = todays_date.split('-')
	date_url = ''.join(date_split)
	return date_url