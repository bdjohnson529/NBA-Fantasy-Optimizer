#The Porzingis Script
#Author: Owen Auch, Ben Johnson

from NBA_Fantasy_Backend.NBAFantasyFunctions import *
from NBA_Fantasy_Backend.ScrollableFrame import Scrollable
from pathlib2 import Path

from copy import deepcopy
import cv2
import PIL.Image, PIL.ImageTk
import Tkinter as tkinter
from Tkinter import Tk, Label, Button, Scrollbar
import tkFont as font

import sys

import logging
from timeit import default_timer as timer

NUM_RECENT_GAMES = 10

salary_path = "/home/ben/NBA-Fantasy-Optimizer/DKSalaries.csv"
injury_list_path = "/home/ben/NBA-Fantasy-Optimizer/historic_stats/injuries.txt"
img_path = "/home/ben/NBA-Fantasy-Optimizer/img/logos/"

save_dir = "/home/ben/NBA-Fantasy-Optimizer/historic_stats"
recent_stats_csv = save_dir + "/nba_recent_" + str(NUM_RECENT_GAMES) + "_games.csv"
season_csv = save_dir + "/season_stats.csv"
injured_file = save_dir + "/injuries.txt"

class App():
	def __init__(self, window, game_list, img_path, salary_path):

		self.salary_file = salary_path

		self.window = window
		self.window.title("Find optimal DraftKings NBA lineups")

		# configure logging
		logging.basicConfig()
		logging.getLogger().setLevel(logging.DEBUG)

		# base window layout consists of header, body and footer
		# we use grid() method to layout window
		self.headerFrame = tkinter.Frame(self.window)
		self.headerFrame.pack()

		self.bodyFrame = None

		self.close_button = Button(self.headerFrame, text="Close Application", command=window.destroy)
		self.close_button.grid(row=0, column=1, sticky='ns')

		self.close_button = Button(self.headerFrame, text="Setup", command=self.configurationPage)
		self.close_button.grid(row=0, column=0, sticky='ns')

		# buttons with team logos
		self.teamButtonList		= []

		self.recentMatchPanel	= None
		self.salaryPathPanel	= None
		self.injuryListPanel	= None
		self.saveEntryPanel		= None

		self.formatted_img_list = []
		self.abbv_list 			= None

		self.game_list 			= game_list
		self.selected_game_list = deepcopy(game_list)
		self.injury_list 		= None

		self.img_path			= img_path
		self.salary_path 		= salary_path

		self.num_recent_games 	= 10

		self.create_image_list()

	def configurationPage(self):

		self.window.title("Configure dataset")

		self.teamButtonList = []

		if self.bodyFrame is not None:
			self.bodyFrame.destroy()

		self.bodyFrame = tkinter.Frame(self.window)
		self.bodyFrame.pack()

		# populate body with frames
		buttonsFrame = tkinter.Frame(self.bodyFrame)
		scrollableButtonsFrame = Scrollable(buttonsFrame, width=32)

		spacingFrame = tkinter.Frame(self.bodyFrame)
		tkinter.Canvas(spacingFrame, width=40, height=100).grid(row=4, column=0, sticky="w")

		actionsFrame = tkinter.Frame(self.bodyFrame)

		buttonsFrame.grid(row=0, column=0, sticky='ns')
		spacingFrame.grid(row=0, column=1, sticky='ns')
		actionsFrame.grid(row=0, column=2, sticky='ns')

		# Create the font for the buttons
		helv36 = font.Font(family='Helvetica', size=12, weight=font.BOLD)

		# Update scrollableButtonsFrame
		# Open one image so we know the width/height to display
		sampleImg = cv2.imread(self.img_path + "cho" + ".png")
		sampleHeight, sampleWidth, no_channels = sampleImg.shape

		team_list = [x for innerlist in self.game_list for x in innerlist]
		for i in range(0, len(team_list)):

			# grid the logos
			row = int(i / 2)
			col = i % 2

			buttonWithLogo = tkinter.Button(scrollableButtonsFrame, width=sampleWidth, height=sampleHeight,
				command= lambda i=i: self.update_selected_games(i))

			self.teamButtonList.append(buttonWithLogo)

			team = team_list[i]
			team_number = self.abbv_list.index(team)

			row = i/2
			col = i%2

			self.teamButtonList[i].config(image=self.formatted_img_list[team_number], width=sampleWidth, height=sampleHeight)
			self.teamButtonList[i].grid(row=row, column=col)

		# Populate the action frame
		tkinter.Label(actionsFrame, text="Save directory:").grid(row=0, column=0, sticky="w")
		saveEntryPanel = tkinter.Entry(actionsFrame, width=50)
		saveEntryPanel.insert(0, save_dir)
		saveEntryPanel.grid(row=1, column=0, sticky="w")
		actionsFrame.rowconfigure(1, minsize=30)
		setattr(self, 'saveEntryPanel', saveEntryPanel)

		tkinter.Label(actionsFrame, text="Location of salary file:").grid(row=2, column=0, sticky="w")
		salaryPathPanel = tkinter.Entry(actionsFrame, width=50)
		salaryPathPanel.insert(0, salary_path)
		salaryPathPanel.grid(row=3, column=0, sticky="w")
		actionsFrame.rowconfigure(3, minsize=30)
		setattr(self, 'salaryPathPanel', salaryPathPanel)

		tkinter.Label(actionsFrame, text="Location of injury list:").grid(row=4, column=0, sticky="w")
		injuryListPanel = tkinter.Entry(actionsFrame, width=50)
		injuryListPanel.insert(0, injury_list_path)
		injuryListPanel.grid(row=5, column=0, sticky="w")
		actionsFrame.rowconfigure(5, minsize=30)
		setattr(self, 'injuryListPanel', injuryListPanel)

		tkinter.Button(actionsFrame, text="Get Injured Players", width = 20, height=1,
			command= self.get_injury_list).grid(row=5, column=1, sticky="w")

		#tkinter.Canvas(actionsFrame, width=20, height=100).grid(row=4, column=0, sticky="w")
		tkinter.Label(actionsFrame, text="Number of recent matches to use:").grid(row=6, column=0, sticky="w")
		recentMatchPanel = tkinter.Entry(actionsFrame)
		recentMatchPanel.insert(0, NUM_RECENT_GAMES)
		recentMatchPanel.grid(row=7, column=0, sticky="w")
		actionsFrame.rowconfigure(7, minsize=30)
		setattr(self, 'recentMatchPanel', recentMatchPanel)

		tkinter.Button(actionsFrame, text="Update settings", width = 20, height=1,
			command= self.update_settings).grid(row=7, column=1, sticky="w")

		tkinter.Canvas(actionsFrame, width=7, height=100).grid(row=8, column=0, sticky="w")

		lineupButtonFrame = tkinter.Frame(actionsFrame)
		lineupButtonFrame.grid(row=9, column=0, sticky='ns')

		tkinter.Button(lineupButtonFrame, text="Lineup from Season", width = 50, height=4, font=helv36,
			command= lambda i=0: self.LineupPage(i)).grid(row=1, column=0, sticky="w")
		tkinter.Button(lineupButtonFrame, text="Lineup from Recent Data", width = 50, height=4, font=helv36,
			command= lambda i=1: self.LineupPage(i)).grid(row=2, column=0, sticky="w")
		tkinter.Button(lineupButtonFrame, text="Lineup from DraftKings Data", width = 50, height=4, font=helv36,
			command= self.DKLineupPage).grid(row=3, column=0, sticky="w")

	def DrawLineupTable(self, frame, lineup_df):

		grouped_df = lineup_df.groupby(['POS'], as_index=False)

		####
		## heading
		####
		nameLabel = Label(frame, text="Player")
		nameLabel.grid(row=0, column=0)

		positionLabel = Label(frame, text="Position")
		positionLabel.grid(row=0, column=1)

		fppgLabel = Label(frame, text="FPPG")
		fppgLabel.grid(row=0, column=2)

		teamLabel = Label(frame, text="Team")
		teamLabel.grid(row=0, column=3)

		salaryLabel = Label(frame, text="Salary")
		salaryLabel.grid(row=0, column=4)

		####
		## data
		####
		rowNum = 0
		for name, group in grouped_df:

			group = group.reset_index(drop=True)


			rows = group.shape[0]
			for i in range(0, rows):
				rowNum = rowNum + 1

				playerName = group.loc[i,"Player"]
				playerNameLabel = Label(frame, text=playerName)
				playerNameLabel.grid(row=rowNum, column=0)

				position = group.loc[i, "POS"]
				positionLabel = Label(frame, text=position)
				positionLabel.grid(row=rowNum, column=1)

				fppg = group.loc[i, "Fppg"]
				fppg = round(fppg, 2)
				fppgLabel = Label(frame, text=fppg)
				fppgLabel.grid(row=rowNum, column=2)

				team = group.loc[i, "Tm"]
				teamLabel = Label(frame, text=team)
				teamLabel.grid(row=rowNum, column=3)

				salary = group.loc[i, "Salary"]
				salaryLabel = Label(frame, text=salary)
				salaryLabel.grid(row=rowNum, column=4)

		sum_fppg = round(lineup_df["Fppg"].sum(), 2)
		sum_salary = lineup_df["Salary"].sum()

		rowNum = rowNum + 2

		sumFPPGLabel = Label(frame, text=sum_fppg)
		sumFPPGLabel.grid(row=rowNum, column=2)

		sumSalaryLabel = Label(frame, text=sum_salary)
		sumSalaryLabel.grid(row=rowNum, column=4)



	def DKLineupPage(self):

		self.window.title("View lineups")

		if self.bodyFrame is not None:
			self.bodyFrame.destroy()

		self.bodyFrame = tkinter.Frame(self.window)
		self.bodyFrame.pack()

		lineup_df_list = self.create_lineup_from_dk()

		i = 0
		for lineup_df in lineup_df_list:
			lineupFrame = tkinter.Frame(self.bodyFrame)
			lineupFrame.grid(row=i/6, column=i%6, sticky='ns')

			self.DrawLineupTable(lineupFrame, lineup_df)

			i = i+1



	def LineupPage(self, option):

		self.window.title("View lineups")

		if self.bodyFrame is not None:
			self.bodyFrame.destroy()

		self.bodyFrame = tkinter.Frame(self.window)
		self.bodyFrame.pack()

		lineup_df = None
		if(option==0):
			print "Creating lineup from season data."
			lineup_df = self.create_lineup_from_season()
		elif(option==1):
			print "Creating lineup from historical data."
			lineup_df = self.create_lineup_from_history()
		elif(option==2):
			print "Creating lineup from DraftKings data."
			lineup_df = self.create_lineup_from_dk()

		playerdataFrame = tkinter.Frame(self.bodyFrame)
		playerdataFrame.grid(row=0, column=0, sticky='ns')

		print "LINEUP ==== "
		print lineup_df

		grouped_df = lineup_df.groupby(['POS'], as_index=False)

		####
		## heading
		####
		nameLabel = Label(playerdataFrame, text="Player")
		nameLabel.grid(row=0, column=0)

		positionLabel = Label(playerdataFrame, text="Position")
		positionLabel.grid(row=0, column=1)

		fppgLabel = Label(playerdataFrame, text="FPPG")
		fppgLabel.grid(row=0, column=2)

		teamLabel = Label(playerdataFrame, text="Team")
		teamLabel.grid(row=0, column=3)

		salaryLabel = Label(playerdataFrame, text="Salary")
		salaryLabel.grid(row=0, column=4)

		####
		## data
		####
		rowNum = 0
		for name, group in grouped_df:

			group = group.reset_index(drop=True)


			rows = group.shape[0]
			for i in range(0, rows):
				rowNum = rowNum + 1

				playerName = group.loc[i,"Player"]
				playerNameLabel = Label(playerdataFrame, text=playerName)
				playerNameLabel.grid(row=rowNum, column=0)

				position = group.loc[i, "POS"]
				positionLabel = Label(playerdataFrame, text=position)
				positionLabel.grid(row=rowNum, column=1)

				fppg = group.loc[i, "Fppg"]
				fppg = round(fppg, 2)
				fppgLabel = Label(playerdataFrame, text=fppg)
				fppgLabel.grid(row=rowNum, column=2)

				team = group.loc[i, "Tm"]
				teamLabel = Label(playerdataFrame, text=team)
				teamLabel.grid(row=rowNum, column=3)

				salary = group.loc[i, "Salary"]
				salaryLabel = Label(playerdataFrame, text=salary)
				salaryLabel.grid(row=rowNum, column=4)

		sum_fppg = round(lineup_df["Fppg"].sum(), 2)
		sum_salary = lineup_df["Salary"].sum()

		rowNum = rowNum + 2

		sumFPPGLabel = Label(playerdataFrame, text=sum_fppg)
		sumFPPGLabel.grid(row=rowNum, column=2)

		sumSalaryLabel = Label(playerdataFrame, text=sum_salary)
		sumSalaryLabel.grid(row=rowNum, column=4)


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

	def get_injury_list(self):
		injuryListFile = self.injuryListPanel.get()

		injury_list = []
		with open(injured_file, 'r') as f:

			players = f.readlines()
			for player in players:
				injury_list.append(player.strip())

		self.injury_list = injury_list

		print "Injured players = ", injury_list


	def check_files(self, salaryFilePath):
		salary_file = Path(salaryFilePath)
		if not salary_file.is_file():
			return False
		else:
			return True

	def create_lineup_from_dk(self):


		if not self.check_files(self.salary_file):
			print "No salary file found. Please download salary CSV from DraftKings"

		print "--------------------------"
		print "Creating lineup based on DraftKings data"

		dk_df = pandas.read_csv(salary_file)

		columnNames = dk_df.columns.tolist()
		columnNames[2] = 'Player'
		columnNames[4] = 'Pos Options'
		columnNames[7] = 'Tm'
		columnNames[8] = 'Fppg'

		dk_df.columns = columnNames

		dk_df['SG'] = 0
		dk_df['PG'] = 0
		dk_df['G'] = 0
		dk_df['C'] = 0
		dk_df['SF'] = 0
		dk_df['PF'] = 0
		dk_df['F'] = 0
		dk_df['UTIL'] = 1

		for index, row in dk_df.iterrows():
			posOptions = row['Pos Options'].split('/')

			if('SG' in posOptions):
				dk_df.at[index, 'SG'] = 1
			if('PG' in posOptions):
				dk_df.at[index, 'PG'] = 1
			if('G' in posOptions):
				dk_df.at[index, 'G'] = 1
			if('C' in posOptions):
				dk_df.at[index, 'C'] = 1
			if('SF' in posOptions):
				dk_df.at[index, 'SF'] = 1
			if('PF' in posOptions):
				dk_df.at[index, 'PF'] = 1
			if('F' in posOptions):
				dk_df.at[index, 'F'] = 1

		# Crawling the injury list can take up to 11 seconds
		# To save time the user can read injury list from a text file
		if(self.injury_list == None):
			self.injury_list = get_injured_players(self.selected_game_list)

		dk_df = dk_df[~dk_df['Player'].isin(self.injury_list)]
		dk_df = dk_df.reset_index(drop=True)

		dk_df.to_csv("dk.csv", sep=",")

		#opp_scaling_df = self.get_scaling()
		salary_df = self.get_salary()

		lineup_df_list = create_dk_lineup(dk_df)

		return lineup_df_list


	def create_lineup_from_season(self):


		if not self.check_files(self.salary_file):
			print "No salary file found. Please download salary CSV from DraftKings"

		print "--------------------------"
		print "Creating lineup based on season stats"


		#### TIME OPTIMIZATION ####
		## scraping the stats online takes 3.3 seconds
		## reading stats from a csv takes 0.01 seconds
		####

		#call method to get season stats for each player
		#season_df = get_season_stats(season_stat_url)
		#season_df.to_csv(season_csv, sep=",")
		#season_desc_df = get_desc_stats(season_df)

		start = timer()
		season_df = pandas.read_csv(season_csv)#
		end = timer()
		elapsed = (end - start)
		print "TIME TO READ SEASON DF === ", elapsed, " s"

		###########################

		#call method to get advanced stats for each player
		# season_advanced_df = get_season_stats(season_advanced_url)
		# advanced_desc_df = get_desc_stats(season_advanced_df)

		print season_df

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
		#injured_list = get_injured_players(self.selected_game_list)
		injured_list = []
		with open(injured_file, 'r') as f:

			players = f.readlines()
			for player in players:
				injured_list.append(player.strip())


		players_df = players_df[~players_df['Player'].isin(injured_list)]
		players_df = players_df.reset_index(drop=True)

		#opp_scaling_df = self.get_scaling()
		salary_df = self.get_salary()

		lineup_df = create_lineup(players_df, salary_df, self.selected_game_list, scaling=None)

		return lineup_df

	def create_lineup_from_history(self):
		print "--------------------------"
		print "Creating a lineup using data from the past ", self.num_recent_games, " games..."

		# get stats from the most recent X games
		recent_stats  = get_historic_stats(self.selected_game_list, todays_date, x=self.num_recent_games)
		recent_stats.to_csv(recent_stats_csv, sep=",")

		recent_stats = drop_injured_players(self.selected_game_list, recent_stats)

		opp_scaling_df = self.get_scaling()
		salary_df = self.get_salary()
		lineup_df = create_lineup(recent_stats, salary_df, self.selected_game_list, scaling=opp_scaling_df)

		return lineup_df

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

	def execute(self):
		# Set up the GUI
		self.configurationPage()

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

	game_list = []
	todays_date = str(date.today())
	game_list = get_schedule(nba_schedule_url, todays_date)

#	internet = str(sys.argv[1])
#	if(internet == "offline"):
#		with open(save_dir + "/schedule.txt", 'r') as f:
#			ok = f.readlines()
#		# attempt to access text file
#		with open(save_dir + "/schedule.txt", 'r') as f:
#			games = f.readlines()
#			for game in games:
#				teams = game.strip().split("'")
#				match = [teams[1], teams[3]]
#				game_list.append(match)
#	else:
#		# access game list and write to text file
#		game_list = get_schedule(nba_schedule_url, todays_date)
#		f = open(save_dir+"/schedule.txt", "w")
#		for game in game_list:
#			print "GAME == ", str(game)
#			f.write(str(game) + "\n")
#		f.close()

	print "Games played today, ", str(todays_date), " include..."
	print game_list
	print "\n\n"

	myApp = App(tkinter.Tk(), game_list, img_path, salary_path)
	myApp.execute()
