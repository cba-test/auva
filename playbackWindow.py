# -*- coding: utf-8 -*-
"""
playbackWindow

@author: cba

EXPIREMENTAL
layout.py allowed me to figure out the various algorithms required, but it also produced inelegant data structures.
the aim of playbackWindow is to write proper class structure, simplify the data architecture and rewrite any algorithms so the final code is simpler and easier to read
"""

"""
CURRENT ISSUES
margin algorithm is not stable enough - set fixed at 10

bar does not resize to better fit very tall, narrow layouts
control buttons vertical positioning does not modify to fit transition between portrait and landscape
meta areas appear to remain squished after vertical size is reduced

text handling - titleText is not moving, font size needs to be calculated to fit controlArea.titleTextArea.height

bar is not high enough (in landscape)
margin is too narrow

SQUISH
squish happens when controlArea.left <= 0
this means the layout is transitioning to portrait mode
this means several things are happened in sequence
art.top decreases (moves up) until art.top <= window.margin
the controlArea is moving down rapidly until controlArea.top >= art.top + art.height

two further things need to happen
art.height decreases until art.top + art.height = predefined split ratio
barArea.height decreases until it reaches predefined modified ratio
control area element mids adjust to fit

all of these calculations need to happen in the correct order or they may interact unfavourably
"""

from tkinter import *
from tkinter import font

from PIL import Image, ImageFilter, ImageTk, ImageEnhance

global window

class area:
	top = 0
	left = 0
	width = 0
	height = 0
	xmid = 0
	ymid = 0
	xmod = 0
	ymod = 0

	def top_from_mid(self):
		self.top = int(self.ymid - (self.height / 2))

	def left_from_mid(self):
		self.left = int(self.xmid - (self.width / 2))

	def mid_from_top(self):
		self.ymid = int(self.top + (self.height / 2))

	def mid_from_left(self):
		self.xmid = int(self.left - (self.width / 2))

class barArea (area):
	opacity = 50 # sets the opacity for a black bar that overlays the (already darkened) background image

class artArea (area):
	art = area()
	artImage = None
	artOpacity = 100
	margin = 0
	portraitArtSplitRatio = 0.6

	def setArtPosition(self, window):
		if self.width > self.height:
			self.margin = window.margin
			artSize = self.height - (self.margin * 2)

			self.art.top = self.margin
			self.art.left = self.margin
			self.art.width = artSize
			self.art.height = artSize
		else:
			if window.transitionSquish:
				self.margin = window.margin
				artSize = self.height * self.portraitArtSplitRatio
				if artSize > window.controlArea.width - (self.margin * 2):
					artSize = window.controlArea.width - (self.margin * 2)

				self.art.xmid = int(window.controlArea.width / 2)
				self.art.left_from_mid()
				self.art.width = artSize
				self.art.height = artSize
				self.art.top = self.margin
		
			else:
				self.margin = window.margin
				artSize = window.controlArea.width - (self.margin * 2)

				self.art.left = self.margin
				self.art.width = artSize
				self.art.height = artSize
				self.mid_from_top()
				self.art.ymid = self.ymid
				self.art.top_from_mid()
				self.art.top = self.art.top - window.controlArea.ymod
				if self.art.top < self.margin:
					self.art.top = self.margin

class controlArea (area):
	split = 0
	splitRatio = 0.65 # 60% of artArea height
	buttonsMidRatio = 0.68
	buttonsAreaWidthMin = 440
	buttonsAreaWidthMax = 500
	# all MidRatio values are arbitrary
	titleMidRatio = 0.82
	albumMidRatio = 0.52
	artistMidRatio = 0.27
	textHeightModifier = 1
	textOverlapModifier = 10 # measured in pixels

	largeButtonSize = 80
	smallButtonSize = 60
	
	playButtonArea = area()
	nextButtonArea = area()
	previousButtonArea = area()

	titleTextArea = area()
	albumTextArea = area()
	artistTextArea = area()

	def __init__(self):
		self.playButtonArea.height = self.largeButtonSize
		self.playButtonArea.width = self.largeButtonSize

		self.nextButtonArea.height = self.smallButtonSize
		self.nextButtonArea.width = self.smallButtonSize

		self.previousButtonArea.height = self.smallButtonSize
		self.previousButtonArea.width = self.smallButtonSize

		self.setMetaHeight()

	def setMetaHeight(self):
		self.titleTextArea.height = int(45 * self.textHeightModifier)
		self.albumTextArea.height = int(30 * self.textHeightModifier)
		self.artistTextArea.height = int(30 * self.textHeightModifier)

	def checkMetaOverlap(self):
		textOverlap = 0

		titleAlbumGap = (self.albumTextArea.ymid - self.titleTextArea.ymid)
		titleAlbumHeights = int(self.titleTextArea.height / 2 + self.albumTextArea.height / 2) + self.textOverlapModifier

		if  titleAlbumHeights > titleAlbumGap:
			textOverlap = titleAlbumGap - titleAlbumHeights

		albumArtistGap = (self.artistTextArea.ymid - self.albumTextArea.ymid)
		albumArtistHeights = int(self.albumTextArea.height / 2 + self.artistTextArea.height / 2) + self.textOverlapModifier

		if  albumArtistHeights > albumArtistGap:
			if albumArtistGap - albumArtistHeights > textOverlap:
				textOverlap = albumArtistGap - albumArtistHeights

		self.textHeightModifier = self.textHeightModifier + (textOverlap / 300) # okay, so it's a rough calculation, but it works!

	def setSplit(self):
		self.split = int(self.height * self.splitRatio)

	def setButtonsMid(self):
		self.playButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)
		self.nextButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)
		self.previousButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)

		self.playButtonArea.top_from_mid()
		self.nextButtonArea.top_from_mid()
		self.previousButtonArea.top_from_mid()

	def setButtonsPositions(self, window):
		buttonsAreaHeight = self.largeButtonSize
		# expand width to handle two seperate conditions for overlap/non-overlap
		if window.overlap:
			buttonsAreaWidth = window.artArea.art.width
		else:
			buttonsAreaWidth = self.width - (window.margin * 2)

		# check minimum/maximum width
		if buttonsAreaWidth < self.buttonsAreaWidthMin:
			buttonsAreaWidth = self.buttonsAreaWidthMin

		if buttonsAreaWidth > self.buttonsAreaWidthMax:
			buttonsAreaWidth = self.buttonsAreaWidthMax

		buttonsAreaMid = self.top + (self.split * self.buttonsMidRatio)
		buttonsAreaLeft = self.left + int(self.width / 2) - (buttonsAreaWidth / 2)

		controlButtonsInnerMargin = int((self.largeButtonSize - self.smallButtonSize) / 2)
		controlButtonsXmodifier = buttonsAreaWidth * 0.1

		# playButtonArea
		self.playButtonArea.width = self.largeButtonSize
		self.playButtonArea.height = self.largeButtonSize
		self.playButtonArea.left = buttonsAreaLeft + int(buttonsAreaWidth / 2) - (self.largeButtonSize / 2)
		self.playButtonArea.ymid = buttonsAreaMid
		self.playButtonArea.top_from_mid()

		# nextButtonArea
		self.nextButtonArea.width = self.smallButtonSize
		self.nextButtonArea.height = self.smallButtonSize
		self.nextButtonArea.left = buttonsAreaLeft + buttonsAreaWidth - (controlButtonsInnerMargin * 2) - self.nextButtonArea.width - controlButtonsXmodifier
		self.nextButtonArea.ymid = buttonsAreaMid
		self.nextButtonArea.top_from_mid()

		# previousButtonArea
		self.previousButtonArea.width = self.smallButtonSize
		self.previousButtonArea.height = self.smallButtonSize
		self.previousButtonArea.left = buttonsAreaLeft + (controlButtonsInnerMargin * 2) + controlButtonsXmodifier
		self.previousButtonArea.ymid = buttonsAreaMid
		self.previousButtonArea.top_from_mid()

	def setMetaMids(self):
		self.titleTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.titleMidRatio)
		self.albumTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.albumMidRatio)
		self.artistTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.artistMidRatio)

		self.titleTextArea.top_from_mid()
		self.albumTextArea.top_from_mid()
		self.artistTextArea.top_from_mid()

	def setMetaWidth(self, margin):
		self.titleTextArea.left = self.left + margin
		self.titleTextArea.width = self.width - (margin * 2)

		self.albumTextArea.left = self.left + margin
		self.albumTextArea.width = self.width - (margin * 2)

		self.artistTextArea.left = self.left + margin
		self.artistTextArea.width = self.width - (margin * 2)

class playbackWindow:
	top = 0
	left = 0
	width = 0
	height = 0
	ratio = 0
	barSplit = 0
	barSplitRatio = 0.125 # 10% of window height
	barSplitModifier = 0.64 # as layout transitions into portrait mode, barSplitRatio needs to shrink
	margin = 20
	marginRatio = 0.04 # currently set as 4% of the artArea height
	overlap = False
	transitionSquish = False
	controlAreaLock = False
	overlapWidth = 0
	overlapRatio = 0.8 # currently set as controlArea.width >= 80% of (window.height - window.barArea.height)
	transitionAccelerator = 10 # used to ensure controlArea moves into correct portrait positioning

	# declare main areas
	barArea = barArea()
	artArea = artArea()
	controlArea = controlArea()

	def getWindowRatio(self):
		self.ratio = self.width / self.height

	def setBarSplit(self):
		cappedRatio = self.ratio
		if cappedRatio > 1:
			cappedRatio = 1
		elif cappedRatio < self.barSplitModifier:
			cappedRatio =self. barSplitModifier

		self.barSplit = self.height * (self.barSplitRatio * cappedRatio)

	def setOverlap(self):
		self.overlapWidth = (self.height - self.barArea.height) * self.overlapRatio
	
		portraitModeTransitionModifier = 0

		if self.controlArea.width < self.overlapWidth:
			# OVERLAP - controlArea overlaps artArea
			self.overlap = True
			virtualArtArea = self.width - self.overlapWidth
			if virtualArtArea < 0:
				virtualArtArea = 0
			self.artArea.artOpacity = int((virtualArtArea / self.overlapWidth) * 100)

			self.controlArea.top = 0
			self.controlArea.ymod = 0
			self.controlArea.left  = self.width - self.overlapWidth
			self.controlArea.width = self.overlapWidth

			if self.controlArea.left < 0:
				# if controlArea.left < 0 then window is transitioning into portrait mode
				# artwork needs to move to the top of the artArea
				# controlButtons and meta text need to subtly change layout
				print('SQUISH!')
				self.transitionSquish = True
				portraitModeTransitionModifier = self.controlArea.left
				self.controlArea.ymod = -portraitModeTransitionModifier * self.transitionAccelerator
				if self.controlArea.ymod > self.artArea.height:
					self.controlArea.ymod = self.artArea.height
				self.controlArea.top = self.controlArea.ymod

				self.controlArea.left = 0
				self.controlArea.width = self.width

				# check to see if controlArea has moved beneath art
				if (self.artArea.art.top + self.artArea.art.height) <= self.controlArea.top:
					self.controlAreaLock = True
					print('-> controlArea LOCK')
					self.controlArea.top = self.artArea.art.top + self.artArea.art.height
					self.controlArea.height = self.barArea.top - self.controlArea.top
				else:
					self.controlAreaLock = False

				self.artArea.artOpacity = int(self.controlArea.top / ((self.artArea.art.top + self.artArea.art.height) / 100))
			else:
				self.transitionSquish = False
		else:
			# NO OVERLAP - controlArea and artArea are adjoined but seperate
			self.overlap = False
			self.artArea.artOpacity = 100

		self.controlArea.height = self.barArea.top - self.controlArea.top
		self.controlArea.setSplit()

def zones (window):
	# define main areas
	window.getWindowRatio()
	window.setBarSplit()
	window.barArea.left = 0
	window.barArea.width = window.width
	window.barArea.height = int(window.barSplit)
	window.barArea.top = window.height - window.barArea.height

	window.artArea.top = window.top
	window.artArea.left = window.left
	window.artArea.width = int(window.width / 2)
	window.artArea.height = window.barArea.top

	window.controlArea.top = window.top
	window.controlArea.left = window.artArea.width
	window.controlArea.width = window.artArea.width
	window.controlArea.height = window.barArea.top

	window.setOverlap()

	window.artArea.setArtPosition(window)

	window.controlArea.setSplit()
	window.controlArea.setButtonsMid()
	window.controlArea.setButtonsPositions(window)
	window.controlArea.setMetaMids()
	window.controlArea.setMetaWidth(window.margin)
	window.controlArea.checkMetaOverlap()
	window.controlArea.setMetaHeight()

def resizeMainPanel(event):
	global window

	window.width = mainPanel.winfo_width()
	window.height = mainPanel.winfo_height()

	zones(window)

	windowCanvas.config(width=window.width, height=window.height)

	windowCanvas.coords(backgroundRectangle,window.left, window.top, window.width, window.height)

	windowCanvas.coords(barAreaRectangle, window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height)
	windowCanvas.coords(artAreaRectangle, window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height)
	windowCanvas.coords(controlAreaRectangle, window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height)

	windowCanvas.coords(albumArtAreaRectangle, window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height)

	windowCanvas.coords(playButtonAreaRectangle, window.controlArea.playButtonArea.left, window.controlArea.playButtonArea.top, window.controlArea.playButtonArea.left + window.controlArea.playButtonArea.width, window.controlArea.playButtonArea.top + window.controlArea.playButtonArea.height)
	windowCanvas.coords(nextButtonAreaRectangle, window.controlArea.nextButtonArea.left, window.controlArea.nextButtonArea.top, window.controlArea.nextButtonArea.left + window.controlArea.nextButtonArea.width, window.controlArea.nextButtonArea.top + window.controlArea.nextButtonArea.height)
	windowCanvas.coords(previousButtonAreaRectangle, window.controlArea.previousButtonArea.left, window.controlArea.previousButtonArea.top, window.controlArea.previousButtonArea.left + window.controlArea.previousButtonArea.width, window.controlArea.previousButtonArea.top + window.controlArea.previousButtonArea.height)
	
	windowCanvas.coords(titleTextAreaRectangle, window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height)
	windowCanvas.coords(albumTextAreaRectangle, window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height)
	windowCanvas.coords(artistTextAreaRectangle, window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height)

	windowCanvas.coords(titleText, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top)
	windowCanvas.coords(albumText, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top)
	windowCanvas.coords(artistText, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top)

	windowCanvas.update

# declare window
window = playbackWindow()

# define window
window.top = 0
window.left = 0
window.width = 1280
window.height = 800

zones(window)

print('Window: ', window.top, window.left, window.width, window.height)
print('window.barArea: ', window.barArea.left, window.barArea.top, window.barArea.width, window.barArea.height)
print('window.artArea: ', window.artArea.top, window.artArea.left, window.artArea.width, window.artArea.height)
print('window.controlArea: ', window.controlArea.top, window.controlArea.left, window.controlArea.width, window.controlArea.height)
print('window.controlArea.titleTextArea: ', window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.height)

# init mainPanel
mainPanel = Tk()

playButtonPNG = Image.open("png/play_button.png")
playButtonImage = ImageTk.PhotoImage(playButtonPNG)

forwardButtonPNG = Image.open("png/forward_button.png")
forwardButtonImage = forwardButtonPNG

backButtonPNG = Image.open("png/back_button.png")
backButtonImage = backButtonPNG

mainPanel.title('Auva')
mainPanel.minsize(480, 480)
mainPanelGeometry = str(window.width) + 'x' + str(window.height)
mainPanel.geometry(mainPanelGeometry)
# mainPanel.resizable(False, False)
# mainPanel.attributes("-topmost", True)

windowCanvas = Canvas(mainPanel, width = window.width, height = window.height, bd=0, highlightthickness=0)
windowCanvas.pack()

# background rectangle
backgroundRectangle = windowCanvas.create_rectangle(window.left, window.top, window.width, window.height, width=0, fill="#222222")

# barArea rectangle
barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="blue")
# barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="#111111")

# artArea rectangle
artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="red")
# artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="#222222")

# controlArea rectangle
controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="green")
# controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="#222222")

# albumArtArea rectangle
albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0, fill="yellow")
# albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0)

# playButtonArea
playButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.playButtonArea.left, window.controlArea.playButtonArea.top, window.controlArea.playButtonArea.left + window.controlArea.playButtonArea.width, window.controlArea.playButtonArea.top + window.controlArea.playButtonArea.height, width=0, fill="grey")

# nextButtonArea
nextButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.nextButtonArea.left, window.controlArea.nextButtonArea.top, window.controlArea.nextButtonArea.left + window.controlArea.nextButtonArea.width, window.controlArea.nextButtonArea.top + window.controlArea.nextButtonArea.height, width=0, fill="grey")

# previousButtonArea
previousButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.previousButtonArea.left, window.controlArea.previousButtonArea.top, window.controlArea.previousButtonArea.left + window.controlArea.previousButtonArea.width, window.controlArea.previousButtonArea.top + window.controlArea.previousButtonArea.height, width=0, fill="grey")

# titleTextArea rectangle
titleTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height, width=0, fill="grey")
# titleTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height, width=0)

titleFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.titleTextArea.height, weight="normal")
titleText = windowCanvas.create_text(window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top, anchor='ne', justify='right', text='Art3mis & Parzival', font=titleFont, fill='white')

# albumTextArea rectangle
albumTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height, width=0, fill="grey")
# albumTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height, width=0)

albumFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.albumTextArea.height, weight="normal")
albumText = windowCanvas.create_text(window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top, anchor='ne', justify='right', text='Dark All Day', font=albumFont, fill='white')

# artistTextArea rectangle
artistTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height, width=0, fill="grey")
# artistTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height, width=0, fill="black")

artistFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.artistTextArea.height, weight="normal")
artistText = windowCanvas.create_text(window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top, anchor='ne', justify='right', text='Gunship', font=artistFont, fill='white')

mainPanel.bind( "<Configure>", resizeMainPanel)

mainPanel.mainloop()