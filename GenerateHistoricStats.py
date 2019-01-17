#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from NBA_Fantasy_Backend.NBAFantasyFunctions import *
from pathlib2 import Path

NUM_RECENT_GAMES = 10
DATE_OF_INTEREST = "2019-01-16"
HISTORIC_DATE = "2019-01-15"

save_dir = "C:\\Users\\OKSI\\Documents\\NBA-Fantasy-Optimizer\\Historic_Stats"
daily_csv = save_dir + "\\daily_" + DATE_OF_INTEREST + ".csv"
historic_csv = save_dir + "\\historic_" + HISTORIC_DATE + "_back_" + str(NUM_RECENT_GAMES) + "_games.csv"

if __name__ == "__main__":

	# Test that CSV files can be edited
	csv_list = [daily_csv, historic_csv]
	for file in csv_list:
		try:
			myfile = open(historic_csv, "w+") # or "a+", whatever you need
		except IOError:
			print "\nCould not open file! Please close Excel!"
			exit()


	print "\n\n\n\n@@@@@@@@@@@@@@@@@@ Let's Analyze NBA Data @@@@@@@@@@@@@@@@@@@@@"

	print "\nPerforming analysis on historic data...\n\n"

	game_list = get_schedule(nba_schedule_url, DATE_OF_INTEREST)
	print "Games played on this day, ", str(DATE_OF_INTEREST), " include..."
	print game_list
	print "\n\n"

	# get stats on the historic day
	daily_stats = get_historic_stats(game_list, DATE_OF_INTEREST, x=1)
	ppg_daily = get_ppg(daily_stats)
	ppg_daily.to_csv(daily_csv, sep=",")

	print "\n\n\n*************** STATS ON THE DAY OF ", DATE_OF_INTEREST, "********************"
	print daily_stats
	print "--------------------------"
	print "Predicting performances for players based on " + str(NUM_RECENT_GAMES) + " previous games..."

	# get stats from the most recent X games
	X = NUM_RECENT_GAMES
	recent_stats  = get_historic_stats(game_list, HISTORIC_DATE, x=X)
	ppg_df = get_ppg(recent_stats)
	ppg_df.to_csv(historic_csv, sep=",")
	print "Results saved to file."

	print "*************** HISTORIC STATS BEFORE THE DAY OF ", HISTORIC_DATE, "********************"
	print recent_stats