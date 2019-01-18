#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from NBA_Fantasy_Backend.NBAFantasyFunctions import *
from NBA_Fantasy_Backend.GUI_DKFantasyLineup import *
from pathlib2 import Path

NUM_RECENT_GAMES = 10

from tkinter import Tk, Label, Button
import logging

salary_path = "C:\\Users\\OKSI\\Documents\\NBA-Fantasy-Optimizer\\DKSalaries.csv"
img_path = "C:\\Users\\OKSI\\Documents\\NBA-Fantasy-Optimizer\\img\\logos\\"

save_dir = "C:\\Users\\OKSI\\Documents\\NBA-Fantasy-Optimizer\\Historic_Stats"
recent_stats_csv = save_dir + "\\nba_recent_" + str(NUM_RECENT_GAMES) + "_games.csv"

if __name__ == "__main__":

	# configure logging
	logging.basicConfig()
	logging.getLogger().setLevel(logging.DEBUG)
	logging.debug("Program starting.")

	print "\n\n\n\n@@@@@@@@@@@@@@@@@@ Let's Analyze NBA Data @@@@@@@@@@@@@@@@@@@@@"

	'''
	First check for files
	'''

	try:
		myfile = open(recent_stats_csv, "w") # or "a+", whatever you need
	except IOError:
		print "Could not open file! Please close Excel!"
		exit()

	salary_file = Path(salary_path)
	if not salary_file.is_file():
		print "No salary file found. Please download salary CSV from DraftKings"
		exit()

	'''
	Begin program
	'''

	print "\nFetching NBA statistics and determining optimal lineup...\n\n"

	todays_date = str(date.today())
	game_list = get_schedule(nba_schedule_url, todays_date)
	print "Games played today, ", str(todays_date), " include..."
	print game_list
	print "\n\n"

	selection_gui = SelectTeamsWindow(tkinter.Tk(), game_list, img_path)
	selection_gui.execute()


	# call method to get recent stats for teams playing tonight
	opp_scaling_df = get_opp_scaling()

	#call method to get season stats for each player
	season_df = get_season_stats(season_stat_url)
	season_desc_df = get_desc_stats(season_df)

	#call method to get salaries for players playing tonight
	salary_df = get_current_salary(salary_path)
	salary_desc_df = get_desc_stats(salary_df)

	#call method to get advanced stats for each player
	# season_advanced_df = get_season_stats(season_advanced_url)
	# advanced_desc_df = get_desc_stats(season_advanced_df)

	players_data_list = []
	for match in game_list:
		home = match[0]
		away = match[1]

		home_players = season_df.loc[season_df['Tm'] == home]
		players_data_list.append(home_players)
		away_players = season_df.loc[season_df['Tm'] == away]
		players_data_list.append(away_players)

	players_df = pandas.concat(players_data_list, axis=0, ignore_index=True)

	# drop inujured players from table
	players_df = drop_injured_players(game_list, players_df)

	print "--------------------------"
	print "Creating lineup based on season stats"
	create_lineup(players_df, salary_df, game_list, scaling=opp_scaling_df)

	print "--------------------------"
	print "Now for your suggestions using data from the past 10 games..."

	# get stats from the most recent X games
	X = NUM_RECENT_GAMES
	recent_stats  = get_historic_stats(game_list, todays_date, x=10)
	recent_stats.to_csv(recent_stats_csv, sep=",")
	
	recent_stats = drop_injured_players(game_list, recent_stats)

	create_lineup(recent_stats, salary_df, game_list, scaling=opp_scaling_df)