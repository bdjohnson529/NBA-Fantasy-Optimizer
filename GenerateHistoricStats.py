#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from NBA_Fantasy_Backend.NBAFantasyFunctions import *
from pathlib2 import Path

NUM_RECENT_GAMES = 10
HISTORIC_DATE = "2019-01-16"

save_dir = "C:\\Users\\OKSI\\Documents\\NBA-Fantasy-Optimizer\\Historic_Stats"
historic_csv = save_dir + "\\historic_" + HISTORIC_DATE + "_back_" + str(NUM_RECENT_GAMES) + "_games.csv"

if __name__ == "__main__":

	print "\n\n\n\n@@@@@@@@@@@@@@@@@@ Let's Analyze NBA Data @@@@@@@@@@@@@@@@@@@@@"

	print "\nPerforming analysis on historic data...\n\n"

	game_list = get_schedule(nba_schedule_url, HISTORIC_DATE)
	print "Games played on this day, ", str(HISTORIC_DATE), " include..."
	print game_list
	print "\n\n"

	# get stats from the most recent X games
	X = NUM_RECENT_GAMES
	season_df = get_season_stats(season_stat_url)
	recent_stats  = get_recent_stats(game_list, HISTORIC_DATE, season_df, x=X)

	print "RECENT*********************************** "
	print recent_stats

	print "--------------------------"
	print "Predicting performances for players based on " + str(NUM_RECENT_GAMES) + " previous games..."
	ppg_df = get_ppg(recent_stats)
	ppg_df.to_csv(historic_csv, sep=",")
	print "Results saved to file."