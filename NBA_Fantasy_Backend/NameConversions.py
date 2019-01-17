from datetime import date

def teamrankings_name_to_abbreviation(stat_name):

	abb_name = ""

	if(stat_name=="Opponent Offensive Rebounds per Game"):
		abb_name = "ORB"
	elif(stat_name=="Opponent Defensive Rebounds per Game"):
		abb_name = "DRB"
	elif(stat_name=="Opponent Points per Game"):
		abb_name = "PTS"
	elif(stat_name=="Opponent Assists per Game"):
		abb_name = "AST"
	elif(stat_name=="Opponent Turnovers per Game"):
		abb_name = "TOV"
	elif(stat_name=="Opponent Blocks per Game"):
		abb_name = "BLK"
	elif(stat_name=="Opponent Steals per Game"):
		abb_name = "STL"
	elif(stat_name=="Opponent Three Pointers Made per Game"):
		abb_name = "3P"

	return abb_name

def get_yesterdays_url():
	todays_date = str(date.today())

	date_split = todays_date.split("-")
	yesterday = int(date_split[2]) - 1
	date_split[2] = str(yesterday)

	yesterday_url = ''.join(date_split)

	return yesterday_url

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

	lst = [year,month,day]
	date = '-'.join(lst)

	return date

def create_date_url(todays_date):
	date_split = todays_date.split('-')
	date_url = ''.join(date_split)
	return date_url

def convert_team_to_abbreviation(full_name):

	abb = ""

	if("Toronto" in full_name):
		abb = "TOR"
	elif("Atlanta" in full_name):
		abb = "ATL"
	elif("Brooklyn" in full_name):
		abb = "BRK"
	elif("Boston" in full_name):
		abb = "BOS"
	elif("Charlotte" in full_name):
		abb = "CHO"
	elif("Chicago" in full_name):
		abb = "CHI"
	elif("Cleveland" in full_name):
		abb = "CLE"
	elif("Dallas" in full_name):
		abb = "DAL"
	elif("Denver" in full_name):
		abb = "DEN"
	elif("Detroit" in full_name):
		abb = "DET"
	elif("Golden State" in full_name):
		abb = "GSW"
	elif("Houston" in full_name):
		abb = "HOU"
	elif("Indiana" in full_name):
		abb = "IND"
	elif("Lakers" in full_name):
		abb = "LAL"
	elif("Clippers" in full_name):
		abb = "LAC"
	elif("Memphis" in full_name):
		abb = "MEM"
	elif("Miami" in full_name):
		abb = "MIA"
	elif("Milwaukee" in full_name):
		abb = "MIL"
	elif("Minnesota" in full_name):
		abb = "MIN"
	elif("New Orleans" in full_name):
		abb = "NOP"
	elif("New York" in full_name):
		abb = "NYK"
	elif("Okla" in full_name):
		abb = "OKC"
	elif("Orlando" in full_name):
		abb = "ORL"
	elif("Philadelphia" in full_name):
		abb = "PHI"
	elif("Phoenix" in full_name):
		abb = "PHO"
	elif("Portland" in full_name):
		abb = "POR"
	elif("Sacramento" in full_name):
		abb = "SAC"
	elif("San Antonio" in full_name):
		abb = "SAS"
	elif("Toronto" in full_name):
		abb = "TOR"
	elif("Utah" in full_name):
		abb = "UTA"
	elif("Washington" in full_name):
		abb = "WAS"

	return abb