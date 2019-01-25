#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from bs4 import BeautifulSoup, Comment
from BS4Functions import *

import csv
import pandas
from PandasFunctions import *
import random
from copy import deepcopy
import itertools
import math

from sys import version_info
from datetime import date

from NameConversions import *

# Turn off pandas warnings
pandas.options.mode.chained_assignment = None  # default='warn'

#website urls
opp_off_rebounds_url = "https://www.teamrankings.com/nba/stat/opponent-offensive-rebounds-per-game"
opp_def_rebounds_url = "https://www.teamrankings.com/nba/stat/opponent-defensive-rebounds-per-game"
opp_points_url = "https://www.teamrankings.com/nba/stat/opponent-points-per-game"
opp_assists_url = "https://www.teamrankings.com/nba/stat/opponent-assists-per-game"
opp_turnovers_url = "https://www.teamrankings.com/nba/stat/opponent-turnovers-per-game"
opp_blocks_url = "https://www.teamrankings.com/nba/stat/opponent-blocks-per-game"
opp_steals_url = "https://www.teamrankings.com/nba/stat/opponent-steals-per-game"
opp_three_url = "https://www.teamrankings.com/nba/stat/opponent-three-pointers-made-per-game"
season_stat_url = "http://www.basketball-reference.com/leagues/NBA_2019_totals.html"
season_advanced_url = "http://www.basketball-reference.com/leagues/NBA_2019_advanced.html"

nba_schedule_url = "https://www.basketball-reference.com/leagues/NBA_2019_games-january.html"

#DraftKings NBA Classic scoring
POINT = 1
REBOUND = 1.25
ASSIST = 1.5
STEAL = 2
BLOCK = 2
TOV = -0.5
THREE = 0.5

#2 PG, 1 SG, 2 SF, 2 PF, 1 C
salary_cap = 50000
PG_cap = 2
SG_cap = 1
SF_cap = 2
PF_cap = 2
C_cap = 1


'''
NBA Functions
'''

def get_schedule(url, date_of_interest):
	today = convert_date(date_of_interest)
	schedule_soup = soupify(url)
	table = schedule_soup.find('table', class_="stats_table")
	table_body = table.find('tbody')

	game_list = []

	tr = table_body.findChildren('tr')
	for row in tr:
		link = row.find('a')
		date = link.find(text=True)
		if (today in date):
			v_td = row.find('td', {"data-stat":"visitor_team_name"})
			visitor = v_td.find(text=True)

			h_td = row.find('td', {"data-stat":"home_team_name"})
			home = h_td.find(text=True)

			visitor = convert_team_to_abbreviation(visitor)
			home = convert_team_to_abbreviation(home)

			game = [home, visitor]
			game_list.append(game)

	return game_list

def get_injured_players(game_list):

	player_list = []
	for match in game_list:
		for team in match:

			team_url = "https://www.basketball-reference.com/teams/" + team + "/2019.html"
			team_soup = soupify(team_url)

			inj = team_soup.find(attrs={"id":"all_injury"})
			if not inj:
				break

			# beautifulsoup magic
			inj_comment = inj.find(string=lambda text:isinstance(text,Comment))
			inj_soup = BeautifulSoup(inj_comment, "lxml")
			tbody = inj_soup.find('tbody')

			tr = tbody.find_all('tr')

			player_status = []
			for entry in tr:
				player = entry.find('th', attrs={"data-stat":"player"})
				player_name = player.find(text=True)
				status = entry.find('td', attrs={"data-stat":"note"})

				if "Out" in str(status):
					player_list.append(player_name.strip())


	return player_list

def get_box_scores(box_url, team):
	
	# bs4 magic
	box_soup = soupify(box_url)
	table_id = "box_" + team.lower() + "_basic"
	table = box_soup.find('table', attrs={"id":table_id})

	g = open("debug.txt", "w")
	g.write(str(table))

	column_names = []
	table_head = table.find('thead')
	tr = table_head.find_all('tr')
	tr = tr[1]

	for col in tr.find_all("th", attrs={}):
		column_names.append(col.find(text=True))

	# get rid of rank, will be index
	column_names[0] = "Player"

	#get data in list matrix
	#make sure to cast strings to floats
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')


	box_data = []
	for row in rows:
		box_data_row = []

		player = row.find('th')
		name = player.find(text=True)

		cols = row.find_all('td')
		if (not cols or len(cols) == 1):
			continue

		box_data_row.append(name)

		# change minutes to float
		for col in cols[:1]:
			stat = col.find(text=True)

			min_sec = stat.split(":")
			time = float(min_sec[0]) + float(min_sec[1])/60
			box_data_row.append(time)

		# the rest of the stats can be converted to floats
		for col in cols[1:]:
			stat = col.find(text=True)
			if stat is None:
				stat = 0.0
			box_data_row.append(float(stat))

		box_data.append(box_data_row)

	#make into pandas dataframe
	box_df = pandas.DataFrame(box_data, columns=column_names)

	return box_df

def get_historic_team_data(team, cutoff_date, x=10):
	pass

def get_team_summary(team, cutoff_date, x=10):

	yesterdays_url = get_yesterdays_url()
	cutoff_url = create_date_url(cutoff_date)

	if (cutoff_url > yesterdays_url):
		print "Cutoff date specified is too recent. Using yesterday's date instead."
		cutoff_url = yesterdays_url

	print "\n"
	print "Retrieving recent ", team, " data. Starting on ", convert_date_url(cutoff_url), " and back ", x, "games. \n"

	team_url = "https://www.basketball-reference.com/teams/" + team + "/2019_games.html"
	game_soup = soupify(team_url)

	# bs4 magic
	table = game_soup.find('table', attrs={"id":"games"})
	table_body = table.find('tbody')
	tr = table_body.findChildren('tr')

	# create list of box score urls and dates
	date_url_list = []
	for row in tr:
		box_score = row.find('td', {"data-stat":"box_score_text"})
		if not box_score:
			continue

		box_url = box_score.find('a')['href']
		date_url = box_url[11:19]

		date_url_list.append([date_url, box_url])

	# reverse list
	date_url_list = date_url_list[::-1]

	# start searching at the end of the list
	i = 0
	j = 0
	for entry in date_url_list:

		date = entry[0]
		if (date > cutoff_url):
			i = i+1
			continue

		j = i
		break


	# use most recent x games
	recent_urls = date_url_list[j:j+x]

	box_list = []
	player_list = []
	for entry in recent_urls:
		url = entry[1]
		full_url = "https://www.basketball-reference.com" + url

		box_df = get_box_scores(full_url, team)
		box_list.append(box_df)

		date = url[11:-9]

		box_df['Date'] = date

		players = box_df['Player'].tolist()
		player_list = player_list + players

	player_list = list(set(player_list))

	player_summary_list = []
	for player in player_list:
		player_list = []

		for score_df in box_list:
			gameScore = score_df.loc[score_df['Player'] == player]
			player_list.append(gameScore)

		player_df = pandas.concat(player_list, axis=0, ignore_index=True)
		player_df = player_df.reset_index(drop=True)

		gp = len(player_df.index)

		mean_pts = player_df['PTS'].mean()
		mean_orb = player_df['ORB'].mean()
		mean_drb = player_df['DRB'].mean()
		mean_ast = player_df['AST'].mean()
		mean_stl = player_df['STL'].mean()
		mean_blk = player_df['BLK'].mean()
		mean_tov = player_df['TOV'].mean()
		mean_3p  = player_df['3P'].mean()

		mean_fp = (mean_pts * POINT) + ((mean_orb + mean_drb) * REBOUND) + (mean_ast * ASSIST) + (mean_stl * STEAL) + (mean_blk * BLOCK) + (mean_tov * TOV) + (mean_3p * THREE)

		var_pts = player_df['PTS'].var()
		var_orb = player_df['ORB'].var()
		var_drb = player_df['DRB'].var()
		var_ast = player_df['AST'].var()
		var_stl = player_df['STL'].var()
		var_blk = player_df['BLK'].var()
		var_tov = player_df['TOV'].var()
		var_3p  = player_df['3P'].var()

		var_fp = (var_pts * math.pow(POINT,2) ) + ((var_orb + var_drb) * math.pow(REBOUND,2) ) + (var_ast * math.pow(ASSIST,2) ) + (var_stl * math.pow(STEAL,2) ) + (var_blk * math.pow(BLOCK,2) ) + (var_tov * math.pow(TOV,2) ) + (var_3p * math.pow(THREE,2) )

		d = {'Player': [player], 'mean_fp': [mean_fp], 'var_fp': [var_fp]}
		player_summary = pandas.DataFrame(data=d)

		player_summary_list.append(player_summary)

	team_summary = pandas.concat(player_summary_list, axis=0, ignore_index=True)
	team_summary = team_summary.sort_values(by="mean_fp", ascending=False)


	print team_summary
	print "******************"

	return team_summary

def get_historic_stats(game_list, cutoff_date, x=10):

	season_df = get_season_stats(season_stat_url)

	aggregate_list = []
	for match in game_list:
		for team in match:
			#team_recent_df = get_historic_team_data(team, cutoff_date, x=x)
			team_recent_df = get_team_summary(team, cutoff_date, x=x)
			aggregate_list.append(team_recent_df)

	players_recent_df = pandas.concat(aggregate_list, axis=0)
	players_recent_df = players_recent_df.reset_index(drop=True)

	# add position to df
	player_position = season_df[["Player","Pos"]]
	players_recent_df = players_recent_df.merge(player_position, left_on='Player', right_on='Player')

	return players_recent_df

#get stat for each team for 2016 off teamrankings.com
def get_stat_series(url):
	stat_soup = soupify(url)

	#find which stat it is
	title = stat_soup.find('title').string
	first_index = title.find("on")
	second_index = title[first_index + 2:].find("on")
	last_index = first_index + second_index + 1
	stat_cat = title[21:last_index]
	stat_cat = teamrankings_name_to_abbreviation(stat_cat)

	#just get first and second column
	stat_data = []
	team_index = []
	rows = stat_soup.find_all('tr')
	del rows[0]
	for row in rows:
		cols = row.find_all('td')
		full_name = cols[1]['data-sort']
		
		abb_name = convert_team_to_abbreviation(full_name)
		team_index.append(abb_name)
		stat_data.append((float)(cols[2].find(text=True)))

	#get in series and sort it
	stat_series = pandas.Series(stat_data, index=team_index, name=stat_cat)
	stat_series = stat_series.sort_index()

	return stat_series

#get season stats from basketball reference
def get_season_stats(url):
	season_soup = soupify(url)

	#get column names
	column_names = []
	table = season_soup.find('table', class_="stats_table")
	table_head = table.find('thead')
	tr = table_head.find('tr')
	for col in tr.find_all("th"):
		column_names.append(col.find(text=True))

	#get rid of rank, will be index
	del column_names[0]

	#get data in list matrix
	#make sure to cast strings to floats
	rows = season_soup.find_all('tr', class_ = "full_table")
	season_data = []
	for row in rows:
		cols = row.find_all('td')
		season_data_row = []
		for col in cols[0:4]:
			season_data_row.append(col.find(text=True))
		for col in cols[4:]:
			stat = col.find(text=True)
			if stat is None:
				stat = 0.0
			season_data_row.append(float(stat))
		season_data.append(season_data_row)

	#make into pandas dataframe
	season_df = pandas.DataFrame(season_data, columns=column_names)

	return season_df

def get_current_salary(path):

	salary_data = []
	counter = 0

	with open(path, 'rb') as csvfile:
		salary_sheet = csv.reader(csvfile, delimiter=',')
		for row in salary_sheet:
			if counter > 0:
				salary_data_row = []
				#add player name
				player_name = row[2]
				salary_data_row.append(player_name.strip())
				#add salary
				salary = row[5]
				salary_data_row.append(float(salary))
				salary_data.append(salary_data_row)
			counter += 1

	salary_df = pandas.DataFrame(salary_data, columns = ["Player", "Salary"])

	return salary_df

#get mean, standard error dataframe for a dataframe
def get_desc_stats(df):
	means = df.mean()
	means = means.rename({1:"mean"})
	stdevs = df.std()
	stdevs = stdevs.rename({1:"stdev"})
	desc_stats = pandas.concat([means, stdevs], axis=1)
	return desc_stats

#gets df of players playing tonight with "Player", "POS", "PPG", "Salary" columns
def get_simple_ppg(season, salary):
	#loops through each player playing tonight
	player_column = salary['Player']

	list = []

	#goes through all players playing tonight and presents their season stats as a Series
	for idx, player in enumerate(player_column):
		player_series = season.loc[season['Player'] == player].squeeze()

		#screen out ones where it doesn't match -- sorry Lou (Louis) Williams
		player = "unknown"
		ppg = 0
		ppd = 0

		if not(player_series.empty):

			#games played
			gp = float(player_series["G"])

			#points
	 		pts = float(player_series["PTS"])

	 		#offensive rebounds
			orb = float(player_series["ORB"])

			#defensive rebounds
	 		drb = float(player_series["DRB"])

	 		#assists
	 		ast = float(player_series["AST"])

	 		#steals
	 		stl = float(player_series["STL"])

	 		#blocks
	 		blk = float(player_series["BLK"])

	 		#turnovers
			tov = float(player_series["TOV"])

			total_points = (pts * POINT) + ((orb + drb) * REBOUND) + (ast * ASSIST) + (stl * STEAL) + (blk * BLOCK) + (tov * TOV)
			ppg = total_points / gp
			player = player_series["Player"]
			ppd = ppg / float(salary["Salary"][idx])

		row = [player, player_series["Pos"], ppg, ppd, float(salary["Salary"][idx])]

		list.append(row)

	df = pandas.DataFrame(list, columns=["Player", "POS", "PPG", "PPD", "Salary"])
	df_sort = df.sort_values(by="PPD", ascending=False)
	df_out = df_sort[df_sort["PPD"] != 0]

	return df_out

def find_opponent(team, game_list):
	opp = ""
	for match in game_list:
		if team in match[0]:
			opp = match[1]
		elif team in match[1]:
			opp = match[0]

	return opp

def get_scaled_stats(season, scale, game_list):
	print "Scaling stats according to opponent performance over the season"
	player_totals = season[['Player','Pos','Tm','G','MP','3P','ORB','DRB','AST','STL','BLK','TOV','PTS']]
	
	# average stats over games played
	player_ppg = player_totals
	shape = player_ppg.shape
	for i in range(0, shape[0]):
		games = player_ppg.ix[i,4]
		for j in range(5, shape[1]):
			val = player_ppg.ix[i,j]
			player_ppg.ix[i,j] = val / games

	# scale stats by opponent
	stat_list = ['3P','ORB','DRB','AST','STL','BLK','TOV','PTS']
	scale = scale.reset_index()

	shape = player_ppg.shape
	for i in range(0, shape[0]):
		team = player_ppg['Tm'].ix[i]
		opp = find_opponent(team, game_list)

		for stat in stat_list:
			factor = scale.loc[scale['index'] == opp][stat].values
			val = player_ppg[stat].ix[i]
			player_ppg[stat].ix[i] = val * factor

	return player_ppg

	#gets df of players playing tonight with "Player", "POS", "PPG", "Salary" columns
def get_ppg(stats):
	#loops through each player playing tonight
	player_column = stats['Player']

	list = []

	#goes through all players playing tonight and presents their season stats as a Series
	for idx, player in enumerate(player_column):
		player_series = stats.loc[stats['Player'] == player].squeeze()

		#screen out ones where it doesn't match -- sorry Lou (Louis) Williams
		player = "unknown"
		ppg = 0

		if not(player_series.empty):

			#games played
			gp = float(player_series["G"])

			#points
	 		pts = float(player_series["PTS"])

	 		#offensive rebounds
			orb = float(player_series["ORB"])

			#defensive rebounds
	 		drb = float(player_series["DRB"])

	 		#assists
	 		ast = float(player_series["AST"])

	 		#steals
	 		stl = float(player_series["STL"])

	 		#blocks
	 		blk = float(player_series["BLK"])

	 		#turnovers
			tov = float(player_series["TOV"])

			#three pointers
			threept = float(player_series["3P"])

			pts_total = (pts * POINT) + ((orb + drb) * REBOUND) + (ast * ASSIST) + (stl * STEAL) + (blk * BLOCK) + (tov * TOV) + (threept * THREE)

			stats_total = [pts_total, pts, orb, drb, ast, stl, blk, tov]
			stats_pg = [float(x)/gp for x in stats_total]

			player = player_series["Player"]

		row = [player, player_series["Pos"]] + stats_pg

		list.append(row)

	df = pandas.DataFrame(list, columns=["Player", "POS", "PPG", "PT_PG", "ORB_PG", "DRB_PG", "AST_PG", "STL_PG", "BLK_PG", "TOV_PG"])

	# add position to df
	player_team = stats[["Player","Tm"]]
	df = df.merge(player_team, left_on='Player', right_on='Player')

	return df

def get_ppd(player_totals, salary):

	player_ppg = get_ppg(player_totals)

	# calculate PPD
	# possible that merge is not working because rows differ (there is an index missing)
	players_ppd = player_ppg.merge(salary, on='Player')
	players_ppd['PPD'] = players_ppd['PPG'] / players_ppd["Salary"].astype(float)
	players_ppd = players_ppd.sort_values(by="PPD", ascending=False)
	players_ppd = players_ppd[players_ppd["PPD"] != 0]

	return players_ppd


#returns a list of best lineup according to greedy algorithm)
def greedy_knap(avail_players):
	print "******************\n"

	#list is position, cap, count
	PG = ["PG", PG_cap, 0, [], 0]
	SG = ["SG", SG_cap, 0, [], 1]
	SF = ["SF", SF_cap, 0, [], 2]
	PF = ["PF", PF_cap, 0, [], 3]
	C = ["C", C_cap, 0, [], 4]

	squad = [PG, SG, SF, PF, C]

	current_sal = 0

	#first, get best players in terms of ppg
	for i, row in avail_players.iterrows():		
		for position in squad:
			#if it matches the position
			if (row["POS"] == position[0]):
				#if the position isn't full
				if (position[1] > position[2]):
					print "currrent sal = ", current_sal
					print row["Salary"]
					print "cap = ", salary_cap
					#if we can afford him
					if (current_sal + row["Salary"] <= salary_cap):
						#add him to the list for the position
						position[3].append(row["Player"])
						#increase current salary
						current_sal += row["Salary"]
						#increase number at position
						position[2] += 1
						#replace in squad
						squad_pos = position[4]
						squad[squad_pos] = position

						print squad

	print squad

	#now, loop through again by PPD and replace lowest PPG player at a position with a player with higher PPG
	#while staying under salary cap
	#loops through player
	for i, row in avail_players.iterrows():
		for position in squad:
			#if it matches the position
			if (row["POS"] == position[0]):
				#if there are two players at the position, find the one with lower PPG
				player = ""
				player_sal = 0
				player_ppg = 0
				player_slot = 0
				other_player = None

				if len(position[3]) == 2:
					for players in position[3]:
						#get player_1 row
						player_1 = avail_players.loc[avail_players['Player'] == position[3][0]]
						player_1_ppg = player_1["PPG"].values[0]

						#get player 2 row and ppg
						player_2 = avail_players.loc[avail_players['Player'] == position[3][1]]
						player_2_ppg = player_2["PPG"].values[0]

						if (player_1_ppg > player_2_ppg):
							player = player_2["Player"]
							player_sal = player_2["Salary"]
							player_ppg = player_2["PPG"]
							player_slot = 1
							other_player = player_1

						else:
							player = player_1["Player"]
							player_sal = player_1["Salary"]
							player_ppg = player_1["PPG"]
							other_player = player_2

				#if there's one player, just do that
				else:
					player_row = avail_players.loc[avail_players['Player'] == position[3][0]]
					player = player_row["Player"]
					player_sal = player_row["Salary"]
					player_ppg = player_row["PPG"]
					other_player = player_row


				print player_ppg
				print player_sal

				#if the player's ppg is higher than the lowest at their position
				player_ppg = player_ppg.values[0]
				player_sal = player_sal.values[0]
				player = player.values[0]

				print player_ppg
				print player_sal
				print player

				#if it isn't a duplicate
				if (other_player["Player"].values[0] != row["Player"]):
					if (row["PPG"] > player_ppg):

						print "NEW PPG = ", row["PPG"]
						print "OLD PPG = ", player_ppg

						#if we can afford him
						if (row["Salary"] + current_sal - player_sal <= salary_cap):
							#replace the player in the squad
							current_sal = current_sal - player_sal + row["Salary"]
							position[3][player_slot] = row["Player"]
							squad_pos = position[4]
							squad[squad_pos] = position

	#get player names in a list
	best_squad = []
	for pos in squad:
		pos_players = []
		pos_players.append(pos[0])
		pos_players.append(pos[3])

		best_squad.append(pos_players)

	return best_squad

def get_opp_scaling():
	series_list = []

	off_rebounds_series = get_stat_series(opp_off_rebounds_url)
	series_list.append(off_rebounds_series)

	def_rebounds_series = get_stat_series(opp_def_rebounds_url)
	series_list.append(def_rebounds_series)

	opp_points_series = get_stat_series(opp_points_url)
	series_list.append(opp_points_series)

	opp_assists_series = get_stat_series(opp_assists_url)
	series_list.append(opp_assists_series)

	opp_turnovers_series = get_stat_series(opp_turnovers_url)
	series_list.append(opp_turnovers_series)

	opp_blocks_series = get_stat_series(opp_blocks_url)
	series_list.append(opp_blocks_series)

	opp_steals_series = get_stat_series(opp_steals_url)
	series_list.append(opp_steals_series)

	opp_three_series = get_stat_series(opp_three_url)
	series_list.append(opp_three_series)

	# this contains all opponent stats for each category relevant for fantasy basketball
	# columns, in order, are:
	# 'Opponent Offensive Rebounds per Game', 'Opponent Defensive Rebounds per Game',
	# 'Opponent Points per Game', 'Opponent Assists per Game', 'Opponent Turnovers per Game', 'Opponent Blocks per Game', 'Opponent Steals per Game'
	# teams are in alphabetical order
	opp_stat_df = pandas.concat(series_list, axis=1)
	opp_stat_desc = get_desc_stats(opp_stat_df)

	# creating scaling factor using opp stats
	opp_scaling_df = opp_stat_df

	num_cols = len(opp_scaling_df.columns)

	shape = opp_scaling_df.shape
	for i in range(0, shape[1]):
		mean = opp_stat_desc.ix[i,0]
		std = opp_stat_desc.ix[i,1]

		for j in range(0, shape[0]):
			val = opp_scaling_df.ix[j,i]
			opp_scaling_df.ix[j,i] = 1 + (val - mean) * 0.25 / (2*std)

	return opp_scaling_df


	#returns a list of best lineup according to greedy algorithm)
def dk_knapsack(avail_players, squad):
	current_sal = 0

	for position in squad:

		groupby_position = avail_players.groupby(position[0])
		candidates = groupby_position.get_group(1)
		candidates = candidates.sort_values(by=['Fppd'], ascending=False)
		candidates = candidates.reset_index(drop=True)

		for i, row in candidates.iterrows():
			player = row['Player']
			salary = float(row['Salary'])

			used_players = [x[1] for x in squad]
			if (player not in used_players) and (current_sal + salary < salary_cap):

				position[1] = player
				current_sal = current_sal + salary
				break


	return squad

def stringify_lineup(line):
	go_2 = range(2)
	positions = ["Point Guards", "Shooting Guard", "Small Forwards", "Power Forwards", "Center"]

	stringy_line = "Optimal DraftKings Lineup for Today \n \n"

	counter = 0
	for position in positions:
		stringy_line += position
		stringy_line += ": \n"

		pos_players = line[counter][1]

		for player in pos_players:
			stringy_line += player
			stringy_line += "\n"
		
		counter += 1

		stringy_line += "\n"

	return stringy_line

#have injured players taken out of the lineup
def manual_drop(ppg, line, salary):
	py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
	injured = "y"

	while (injured == "y"):
		if py3:
			injured = input("Do you want to drop any of these players? (y/n)\n")
		else:
			injured = raw_input("Do you want to drop any of these players? (y/n)\n")

		injured = injured.lower()

		if (injured == "y"):
			if py3:
		  		player = input("Enter the injured player's name exactly: ")
			else:
		  		player = raw_input("Enter the injured player's name exactly: ")

		  	ppg = ppg[ppg["Player"] != player]

		  	print stringify_lineup(greedy_knap(ppg))

def drop_injured_players(game_list, dataset):
	injured_list = get_injured_players(game_list)

	with open("injured_list.txt", "w") as f:
		for item in injured_list:
			f.write(str(item) + "\n")

	dataset = dataset[~dataset['Player'].isin(injured_list)]
	dataset = dataset.reset_index(drop=True)
	return dataset

def create_lineup(player_dataset, salary_df, game_list, scaling=None):
	#general approach for next part
	#get each player with position, and all scorable categories
	#find expected points scored, and choose best lineup with greedy algorithm (prioritizing for points per game)
	
	player_totals = player_dataset
	if(scaling is not None):
		player_totals = get_scaled_stats(player_dataset, scaling, game_list)

	#player_ppg = get_ppg(player_totals)
	player_ppd = get_ppd(player_totals, salary_df)
	player_ppd = player_ppd.sort_values(by=['PPD'], ascending=True)
	player_ppd.to_csv("player_ppd.csv")

	lineup = greedy_knap(player_ppd)

	playerstats = []
	for position in lineup:
		players = position[1]
		for player in players:
			playerstats.append( player_ppd.loc[player_ppd['Player'] == player] )
			print "PLAYER == ", player
			print playerstats

	lineup_df = pandas.concat(playerstats, axis=0, ignore_index=True)
	
	#print player_ppd.head()

	return lineup_df

#	pretty_lineup = stringify_lineup(lineup)
#	print pretty_lineup
#	uninjured_pretty = manual_drop(player_ppd, pretty_lineup, salary_df)

def create_dk_lineup(dk_dataset):

	dk_dataset['Fppd'] = dk_dataset['Fppg'] / dk_dataset['Salary'].astype(float)
	dk_dataset = dk_dataset.sort_values(by="Fppd", ascending=False)
	dk_dataset = dk_dataset[dk_dataset["Fppd"] != 0]

	dk_dataset.to_csv("dk_ppd.csv", sep=",")


	squad = [['SF', None], ['UTIL', None], ['F', None], ['PG', None], ['G', None], ['C', None], ['SG', None], ['PF', None]]

	#squad_list = [squad]
	squad_list = list(itertools.permutations(squad))
	lineup_df_list = []
	#for i in range(0,24):


	i = 0
	maxFPPG = 0

	# we use a random permutation of the squad selection order to find the maximum fpp/team
	numPermutations = 300
	if(True):
		squad_list = []
		for i in range(0,numPermutations):
			newSquad = deepcopy(squad)
			random.shuffle(newSquad)
			squad_list.append(newSquad)

		for squad in squad_list:
			lineup = dk_knapsack(dk_dataset, squad)#

			playerstats = []
			for position in lineup:
				player = position[1]
				stats = dk_dataset.loc[dk_dataset['Player'] == player]
				stats['POS'] = position[0]
				playerstats.append(stats)

			lineup_df = pandas.concat(playerstats, axis=0, ignore_index=True)
			sum_fppg = round(lineup_df["Fppg"].sum(), 2)
			salary = float(lineup_df["Salary"].sum())

			if(sum_fppg > maxFPPG) and (salary < salary_cap):
				maxFPPG = sum_fppg
				print "max fppg: ", maxFPPG, " salary = ", salary

	print "Building squad list"
	for squad in squad_list:
		# now find 24 highest fppg squads
		if(len(lineup_df_list) > 23):
			break

		lineup = dk_knapsack(dk_dataset, squad)

		playerstats = []
		for position in lineup:
			player = position[1]
			stats = dk_dataset.loc[dk_dataset['Player'] == player]
			stats['POS'] = position[0]
			playerstats.append(stats)

		lineup_df = pandas.concat(playerstats, axis=0, ignore_index=True)
		sum_fppg = round(lineup_df["Fppg"].sum(), 2)
		salary = float(lineup_df["Salary"].sum())

		if(sum_fppg > maxFPPG - 5) and (salary < salary_cap):
			print "Found squad with ffpg = ", sum_fppg
			lineup_df_list.append(lineup_df)

	print "Found 24 squads. Building tables."

	return lineup_df_list
