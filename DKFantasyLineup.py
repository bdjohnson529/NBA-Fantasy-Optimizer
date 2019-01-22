#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from NBA_Fantasy_Backend.NBAFantasyFunctions import *
from pathlib2 import Path

from copy import deepcopy
import cv2
import PIL.Image, PIL.ImageTk
import Tkinter as tkinter
from Tkinter import Tk, Label, Button, Scrollbar
import tkFont as font

import logging

NUM_RECENT_GAMES = 10

salary_path = "/home/ben/NBA-Fantasy-Optimizer/DKSalaries.csv"
img_path = "/home/ben/NBA-Fantasy-Optimizer/img/logos/"

save_dir = "/home/ben/NBA-Fantasy-Optimizer/historic_stats"
recent_stats_csv = save_dir + "/nba_recent_" + str(NUM_RECENT_GAMES) + "_games.csv"


class App():
	def __init__(self, window, game_list, img_path, salary_path):

		self.window = window
		scrollbar = Scrollbar(window)
		scrollbar.pack( side="right", fill="y" )

		window.title("Find optimal DraftKings NBA lineups")

		# configure logging
		logging.basicConfig()
		logging.getLogger().setLevel(logging.DEBUG)


		self.label = Label(window, text="Select which games you are playing today.")
		self.label.pack()

		self.close_button = Button(window, text="Close Application", command=window.destroy)
		self.close_button.pack()

		self.imagesFrame 		= None

		# buttons with team logos
		self.teamButtonList		= []

		self.recentMatchPanel	= None
		self.salaryPathPanel	= None
		self.saveEntryPanel		= None

		self.formatted_img_list = []
		self.abbv_list 			= None

		self.game_list 			= game_list
		self.selected_game_list = deepcopy(game_list)
		self.img_path			= img_path
		self.salary_path 		= salary_path

		self.num_recent_games 	= 10

	def update_settings(self):
		recentMatchesString = self.recentMatchPanel.get()
		salaryPathString 	= self.salaryPathPanel.get()
		saveString 			= self.saveEntryPanel.get()

		try:
			i = int(recentMatchesString)
			if(i>0 and i<200):
				self.num_recent_games = i
				print "Using ", i, " recent games in the historical model."
			else:
				print "Number out of range. Please enter an integer between 1 and 200."
		except ValueError:
			#Handle the exception
			print 'Please enter an integer.'

		if not self.check_files(salaryPathString):
			print "No salary file found. Please download salary CSV from DraftKings"
		else:
			self.salary_path = salaryPathString

	def check_files(self, salaryFilePath):
		salary_file = Path(salaryFilePath)
		if not salary_file.is_file():
			return False
		else:
			return True


	def create_lineup_from_season(self):
		if not self.check_files(self.salary_file):
			print "No salary file found. Please download salary CSV from DraftKings"

		print "--------------------------"
		print "Creating lineup based on season stats"

		#call method to get season stats for each player
		season_df = get_season_stats(season_stat_url)
		season_desc_df = get_desc_stats(season_df)


		#call method to get advanced stats for each player
		# season_advanced_df = get_season_stats(season_advanced_url)
		# advanced_desc_df = get_desc_stats(season_advanced_df)

		players_data_list = []
		for match in self.selected_game_list:
			home = match[0]
			away = match[1]

			home_players = season_df.loc[season_df['Tm'] == home]
			players_data_list.append(home_players)
			away_players = season_df.loc[season_df['Tm'] == away]
			players_data_list.append(away_players)

		players_df = pandas.concat(players_data_list, axis=0, ignore_index=True)

		# drop inujured players from table
		players_df = drop_injured_players(self.selected_game_list, players_df)

		opp_scaling_df = self.get_scaling()
		salary_df = self.get_salary()
		create_lineup(players_df, salary_df, self.selected_game_list, scaling=opp_scaling_df)

	def create_lineup_from_history(self):
		print "--------------------------"
		print "Creating a lineup using data from the past ", self.num_recent_games, " games..."

		# get stats from the most recent X games
		recent_stats  = get_historic_stats(self.selected_game_list, todays_date, x=self.num_recent_games)
		recent_stats.to_csv(recent_stats_csv, sep=",")
		
		recent_stats = drop_injured_players(self.selected_game_list, recent_stats)

		opp_scaling_df = self.get_scaling()
		salary_df = self.get_salary()
		create_lineup(recent_stats, salary_df, self.selected_game_list, scaling=opp_scaling_df)

	def get_scaling(self):		
		# call method to get recent stats for teams playing tonight
		opp_scaling_df = get_opp_scaling()
		return opp_scaling_df

	def get_salary(self):
		#call method to get salaries for players playing tonight
		salary_df = get_current_salary(self.salary_path)
		return salary_df

	def create_image_list(self):

		self.abbv_list = get_abbreviation_list()
		for entry in self.abbv_list:
			img_filepath = self.img_path + entry.lower() + ".png"

			img = cv2.imread(img_filepath, cv2.IMREAD_COLOR)
			formatted_img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
			self.formatted_img_list.append(formatted_img)	


	def update_selected_games(self, team_num):

		i = team_num/2

		if(self.selected_game_list[i] is not None):
			self.selected_game_list[i] = None
		else:
			print self.game_list[i]
			self.selected_game_list[i] = self.game_list[i]

		print "Selected games = ", self.selected_game_list

	def createWidgets(self, game_list):

		# Initializing function
		self.create_image_list()

		# Create the font for the buttons
		helv36 = font.Font(family='Helvetica', size=12, weight=font.BOLD)

		# Create a frame for each of the different widgets in the GUI
		# We use the grid method to group the frames
		imagesFrame = tkinter.Frame(self.window)
		imagesFrame.pack(side="left")

		spacingFrame = tkinter.Frame(self.window)
		spacingFrame.pack(side="left")
		tkinter.Canvas(spacingFrame, width=40, height=100).grid(row=4, column=0, sticky="w")

		actionsFrame = tkinter.Frame(self.window)
		actionsFrame.pack(side="left")

		# Now fill up the action frame
		tkinter.Label(actionsFrame, text="Save directory:").grid(row=0, column=0, sticky="w")
		saveEntryPanel = tkinter.Entry(actionsFrame, width=50)
		saveEntryPanel.insert(0, save_dir)
		saveEntryPanel.grid(row=1, column=0, sticky="w")
		actionsFrame.rowconfigure(1, minsize=50)
		setattr(self, 'saveEntryPanel', saveEntryPanel)

		tkinter.Label(actionsFrame, text="Location of salary file:").grid(row=2, column=0, sticky="w")
		salaryPathPanel = tkinter.Entry(actionsFrame, width=50)
		salaryPathPanel.insert(0, salary_path)
		salaryPathPanel.grid(row=3, column=0, sticky="w")
		actionsFrame.rowconfigure(3, minsize=50)
		setattr(self, 'salaryPathPanel', salaryPathPanel)

		#tkinter.Canvas(actionsFrame, width=20, height=100).grid(row=4, column=0, sticky="w")
		tkinter.Label(actionsFrame, text="Number of recent matches to use:").grid(row=4, column=0, sticky="w")
		recentMatchPanel = tkinter.Entry(actionsFrame)
		recentMatchPanel.insert(0, NUM_RECENT_GAMES)
		recentMatchPanel.grid(row=5, column=0, sticky="w")
		actionsFrame.rowconfigure(5, minsize=50)
		setattr(self, 'recentMatchPanel', recentMatchPanel)

		tkinter.Button(actionsFrame, text="Update settings", width = 25, height=2, font=helv36,
			command= self.update_settings).grid(row=6, column=0, sticky="w")

		tkinter.Canvas(actionsFrame, width=40, height=100).grid(row=7, column=0, sticky="w")

		tkinter.Button(actionsFrame, text="Lineup from Season", width = 50, height=4, font=helv36,
			command= self.create_lineup_from_season).grid(row=8, column=0, sticky="w")
		tkinter.Button(actionsFrame, text="Lineup from Recent Data", width = 50, height=4, font=helv36,
			command= self.create_lineup_from_history).grid(row=9, column=0, sticky="w")


		# Set up the imagesFrame with canvases for our RGB and masked images
		# Open one image so we know the width/height to display
		sampleImg = cv2.imread(self.img_path + "cho" + ".png")
		sampleHeight, sampleWidth, no_channels = sampleImg.shape

		team_list = [x for innerlist in game_list for x in innerlist]

		# Set up the buttons with team logos
		for i in range(0, len(team_list)):

			# grid the logos
			row = int(i / 2)
			col = i % 2

			buttonWithLogo = tkinter.Button(imagesFrame, width=sampleWidth, height=sampleHeight,
				command= lambda i=i: self.update_selected_games(i))

			self.teamButtonList.append(buttonWithLogo)

			team = team_list[i]
			team_number = self.abbv_list.index(team)

			row = i/2
			col = i%2

			self.teamButtonList[i].config(image=self.formatted_img_list[team_number], width=sampleWidth, height=sampleHeight)
			self.teamButtonList[i].grid(row=row, column=col)

	def execute(self):
		# Set up the GUI
		self.createWidgets(self.game_list)
		#Execute the window's main loop
		self.window.mainloop()





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

	'''
	Begin program
	'''

	print "\nFetching NBA statistics and determining optimal lineup...\n\n"

	todays_date = str(date.today())
	game_list = get_schedule(nba_schedule_url, todays_date)
	print "Games played today, ", str(todays_date), " include..."
	print game_list
	print "\n\n"

	myApp = App(tkinter.Tk(), game_list, img_path, salary_path)
	myApp.execute()
