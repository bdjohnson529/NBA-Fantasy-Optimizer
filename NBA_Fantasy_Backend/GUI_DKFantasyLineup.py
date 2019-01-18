import cv2
import PIL.Image, PIL.ImageTk
import tkinter
from tkinter import Tk, Label, Button

import logging

class SelectTeamsWindow():
	def __init__(self, master, game_list, img_path):

		# = window

		# configure logging
		logging.basicConfig()
		logging.getLogger().setLevel(logging.DEBUG)


		self.master = master
		master.title("A simple GUI")

		self.label = Label(master, text="Select which games you are playing -----")
		self.label.pack()

		self.greet_button = Button(master, text="Greet", command=self.greet)
		self.greet_button.pack()

		self.close_button = Button(master, text="Close", command=master.destroy)
		self.close_button.pack()

		self.close_button = Button(master, text="Close", command=master.destroy)
		self.close_button.pack()

		self.canvasMatch1		= None
		self.canvasMatch2		= None
		self.canvasMatch3		= None
		self.canvasMatch4		= None
		self.canvasMatch5		= None
		self.canvasMatch6		= None
		self.canvasMatch7		= None
		self.canvasMatch8		= None
		self.canvasMatch9		= None
		self.canvasMatch10		= None

		self.game_list 			= game_list
		self.img_path			= img_path

		print "END OF INIT"



	def greet(self):
		print("Greetings!")


	def createWidgets(self, game_list):

		# Create a frame for each of the different widgets in the GUI
		self.menuFrame = tkinter.Frame()
		self.labelFrame = tkinter.Frame()
		imagesFrame = tkinter.Frame()
		buttonFrame = tkinter.Frame()

		# Pack the frames
		self.menuFrame.pack(side="top", fill="both", expand=False)
		self.labelFrame.pack(side="top", fill="both", expand=True)
		imagesFrame.pack(side="top", fill="both", expand=True)
		buttonFrame.pack(side="bottom", fill="both", expand=True)

		# Set up the imagesFrame with canvases for our RGB and masked images
		# Open one image so we know the width/height to display
		sampleImg = cv2.imread(self.img_path + "cho" + ".png")
		height, width, no_channels = sampleImg.shape
		# Set up the RGB and Masked Canvases to expect images half the size of the full image
		self.rgbCanvas = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		self.rgbCanvas.pack(side="left", fill="both", expand=True)
		self.maskedCanvas = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		self.maskedCanvas.pack(side="right", fill="both", expand=True)
	
		# game_list
		# [['CHO', 'SAC'], ['DEN', 'CHI'], ['IND', 'PHI'], ['OKC', 'LAL'], ['TOR', 'PHO'], ['WAS', 'NYK']]

		num_matches = len(game_list)

		#for i in range(0,num_matches):

		match = game_list[0]

		home = match[0]
		away = match[1]

		home_filepath = self.img_path + home.lower() + ".png"
		away_filepath = self.img_path + away.lower() + ".png"

		print home_filepath

		home_img = cv2.imread(home_filepath, cv2.IMREAD_COLOR)
		away_img = cv2.imread(away_filepath, cv2.IMREAD_COLOR)

		# Use pillow to convert the numpy array to a PhotoImage
		self.homeImg = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(home_img))	
		self.awayImg = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(away_img))

		team1 = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		team1.pack(side="left", fill="both", expand=True)
		team2 = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		team2.pack(side="right", fill="both", expand=True)
		self.canvasMatch1 = [team1, team2]

		# Add the images to our canvas
		team1.create_image(0, 0, image=self.homeImg, anchor=tkinter.NW)		
		team2.create_image(0,0, image=self.awayImg, anchor=tkinter.NW)

		# Set up the RGB and Masked Canvases to expect images half the size of the full image
		self.team = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		self.rgbCanvas.pack(side="left", fill="both", expand=True)
		self.maskedCanvas = tkinter.Canvas(imagesFrame, width=width/2, height=height/2)
		self.maskedCanvas.pack(side="right", fill="both", expand=True)

		print "END OF FUNCTION"

	def execute(self):
		logging.debug("SelectTeamsWindow exec()")

		# Set up the GUI
		self.createWidgets(self.game_list)

		return False