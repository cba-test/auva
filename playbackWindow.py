# -*- coding: utf-8 -*-
"""
playbackWindow

@author: cba

EXPIREMENTAL
layout.py allowed me to figure out the various algorithms required, but it also produced inelegant data structures.
the aim of playbackWindow is to write proper class structure, simplify the data architecture and rewrite any algorithms so the final code is simpler and easier to read
"""

from tkinter import *

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
		self.top = self.ymid - int(self.height / 2)

	def left_from_mid(self):
		self.left = self.xmid - int(self.width / 2)

	def mid_from_top(self):
		self.ymid = self.top + int(self.height / 2)

	def mid_from_left(self):
		self.xmid = self.left - int(self.width / 2)

class barArea (area):
	opacity = 50 # sets the opacity for a black bar that overlays the (already darkened) background image

class artArea (area):
	art = area()
	artImage = None
	artOpacity = 100
	margin = 0

	def setArtPosition(self, window):
		# margin = window.margin, controlAreaWidth = window.controlArea.width
		if self.width > self.height:
			self.margin = window.margin
			artSize = self.height - (self.margin * 2)

			self.art.top = self.margin
			self.art.left = self.margin
			self.art.width = artSize
			self.art.height = artSize
		else:
			self.margin = window.margin
			artSize = window.controlArea.width - (self.margin * 2)

			self.art.left = self.margin
			self.art.width = artSize
			self.art.height = artSize
			# SIMPLIFY - for initial testing
			self.art.top = int((self.height - self.art.height) / 2) - window.controlArea.ymod
			# self.art.top = int((self.height - self.art.height) / 2)
			if self.art.top < self.margin:
				self.art.top = self.margin

class controlArea (area):
	split = 0
	splitRatio = 0.6 # 60% of artArea height
	buttonsMidRatio = 0.6
	titleMidRatio = 0.8
	albumMidRatio = 0.45
	artistMidRatio = 0.15
	# all MidRatio values are arbitrary

	playButtonArea = area()
	nextButtonArea = area()
	previousButtonArea = area()

	titleTextArea = area()
	albumTextArea = area()
	artistTextArea = area()

	def __init__(self):
		self.playButtonArea.height = 100
		self.playButtonArea.width = 100

		self.nextButtonArea.height = 80
		self.nextButtonArea.width = 80

		self.previousButtonArea.height = 80
		self.previousButtonArea.width = 80

		self.titleTextArea.height = 60
		self.albumTextArea.height = 40
		self.artistTextArea.height = 40

	def setSplit(self):
		self.split = int(self.height * self.splitRatio)

	def setButtonsMid(self):
		self.playButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)
		self.nextButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)
		self.previousButtonArea.ymid = self.top + int((self.split - self.top) * self.buttonsMidRatio)

		self.playButtonArea.top_from_mid()
		self.nextButtonArea.top_from_mid()
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
	barSplit = 0
	barSplitRatio = 0.1 # 10% of window height
	margin = 0
	marginRatio = 0.04 # currently set as 4% of the artArea height
	overlap = False
	overlapWidth = 0
	overlapRatio = 0.8 # currently set as controlArea.width >= 80% of (window.height - window.barArea.height)
	transitionAccelerator = 3 # used to ensure controlArea moves into correct portrait positioning

	# declare main areas
	barArea = barArea()
	artArea = artArea()
	controlArea = controlArea()

	def setBarSplit(self):
		self.barSplit = self.height * self.barSplitRatio

	def setMargin(self):
		self.margin = int(self.controlArea.width * self.marginRatio)

	def setOverlap(self):
		self.overlapWidth = (self.height - self.barArea.height) * self.overlapRatio
	
		portraitModeTransitionModifier = 0

		if self.controlArea.width < self.overlapWidth:
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
				portraitModeTransitionModifier = self.controlArea.left
				self.controlArea.ymod = -portraitModeTransitionModifier * self.transitionAccelerator
				if self.controlArea.ymod > self.artArea.height:
					self.controlArea.ymod = self.artArea.height
				self.controlArea.top = self.controlArea.ymod

				print('SQUISH!')
				self.controlArea.left = 0
				self.controlArea.width = self.width
		else:
			self.overlap = False
			self.artArea.artOpacity = 100

		self.controlArea.height = self.barArea.top - self.controlArea.top
		self.controlArea.setSplit()

		print('overlapWidth:', self.overlapWidth)
		print('overlap:', self.overlap)
		print('opacity:', self.artArea.artOpacity)

def zones (window):
	# define main areas
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

	window.setMargin()

	window.setOverlap()

	window.artArea.setArtPosition(window)

	window.controlArea.setSplit()
	window.controlArea.setButtonsMid()
	window.controlArea.setMetaMids()
	window.controlArea.setMetaWidth(window.margin)

"""
def landscapeZones(window):
	# define main areas
	# barArea
	window.barArea.left = 0
	window.barArea.width = window.width
	window.barArea.height = int(window.height * 0.1) # set maximum height? extremely high portrait mode looks strange
	# height needs to respect the overall aspect ratio of the window - the smaller the width of the window, the more the bar looks overly high
	if window.barArea.height > 100:
		window.barArea.height = 100
	elif window.barArea.height < 50:
		window.barArea.height = 50
	window.barArea.top = window.height - window.barArea.height

	print('window.barArea.height:',window.barArea.height)

	# artArea
	window.artArea.top = 0
	window.artArea.left = 0
	window.artArea.width = int(window.width / 2)
	window.artArea.height = window.barArea.top

	# controlArea
	window.controlArea.top = window.controlArea.ymod
	window.controlArea.left = window.width - window.artArea.width
	window.controlArea.width = window.artArea.width
	window.controlArea.height = window.barArea.top

	# set generalMargin
	generalMargin = int(window.artArea.height * 0.04)

	# handle overlap
	# 0.8 is 80%, so the minimum width of controlArea should be 80% of the height of window minus the height of the barArea
	minimumControlWidth = 0.8 * (window.height - window.barArea.height)
	print('minimumControlWidth: ', minimumControlWidth)
	portraitModeTransitionModifier = 0
	transitionAccelerator = 3
	if window.controlArea.width < minimumControlWidth:
		virtualArtArea = window.width - minimumControlWidth
		if virtualArtArea < 0:
			virtualArtArea = 0
		albumArtOpacity = int((virtualArtArea / minimumControlWidth) * 100)
		print('Overlap opacity: ',  albumArtOpacity)
		overlap = True

		window.controlArea.top = 0
		window.controlArea.ymod = 0
		window.controlArea.left = window.width - minimumControlWidth
		window.controlArea.width = minimumControlWidth
		if window.controlArea.left < 0:
			# if overlap opacity < 0 then window is transitioning into portrait mode
			# need to define portrait mode so I can define the transition between this point and full portrait mode
			portraitModeTransitionModifier = window.controlArea.left
			window.controlArea.ymod = -portraitModeTransitionModifier * transitionAccelerator
			if window.controlArea.ymod > window.artArea.height:
				window.controlArea.ymod = window.artArea.height
			window.controlArea.top = window.controlArea.ymod

			# if controlArea has completely overlapped artArea, resize to fit window width properly
			window.controlArea.left = 0
			window.controlArea.width = window.width
	else:
		albumArtOpacity = 100
		overlap = False

	window.controlArea.height = window.barArea.top - window.controlArea.top

	# albumArtArea
	if window.artArea.width > window.artArea.height:
		AlbumArtMargin = generalMargin
		AlbumArtSize = window.artArea.height - (AlbumArtMargin * 2)

		window.albumArtArea.top = AlbumArtMargin
		window.albumArtArea.left = AlbumArtMargin
		window.albumArtArea.width = AlbumArtSize
		window.albumArtArea.height = AlbumArtSize
	else:
		AlbumArtMargin = int(window.artArea.width * 0.04)
		# fix albumArtSize when overlap is True
		if overlap:
			AlbumArtSize = window.controlArea.width - (AlbumArtMargin * 2)
		else:
			AlbumArtSize = window.artArea.width - (AlbumArtMargin * 2)

		window.albumArtArea.left = AlbumArtMargin
		window.albumArtArea.width = AlbumArtSize
		window.albumArtArea.height = AlbumArtSize
		window.albumArtArea.top = int((window.artArea.height - window.albumArtArea.width) / 2) - window.controlArea.ymod
		if window.albumArtArea.top < AlbumArtMargin:
			window.albumArtArea.top = AlbumArtMargin

	# upperControlArea and lowerControlArea vertically split the artArea into two parts
	# controls go in upperControlArea, metadata go in lowerControlArea
	# by splitting them up, this allows more dynamic movement between landscape and portrait modes as well as allowing simpler layout rules
	lowerControlAreaHeightPC = 0.3 # 40% of artArea height
	upperControlAreaHeightPCmodifier = 1 # link this modifier to the difference between window.albumArtArea.top + window.albumArtArea.height and window.upperControlArea.top
	# artAreaHeightSplit needs modifier to shrink height when transitioning into portrait mode
	# the same modifier should be applied to the upperControlArea.top and upperControlArea.height values with a further modifier to increase the effect
	# the overall effect should be that the controlButtonArea reduces down to the right placement for true Portrait mode while the metadata stays more or less the same (within scaling constaints)
	print('==========')
	# catch to stop lower/upperControlArea getting too small
	# this also includes a method to adjust the upperControlAreaHeightPCmodifier so that the metadata text doesn't become too small
	# if possible, this should be also be used to adjust the two gaps between the title text/album text and album text/artist text, although this would require a full rewrite of that section
	if window.controlArea.top + window.controlArea.ymod > window.albumArtArea.top + window.albumArtArea.height:
		print('***** FORCE MINIMUM CONTROL AREA HEIGHT *****')
		controlAreaHeightLock = True
		window.upperControlArea.top = window.albumArtArea.top + window.albumArtArea.height
		albumArtFullHeight = window.albumArtArea.top + window.albumArtArea.height 
		controlAreaRatio = (albumArtFullHeight - ((albumArtFullHeight) - window.upperControlArea.top)) / albumArtFullHeight
		print('albumArt:',window.albumArtArea.top + window.albumArtArea.height)
		print('controlAreaRatio:',controlAreaRatio)
		if overlap:
			upperControlAreaHeightPCmodifier = 1 + (controlAreaRatio * 0.4)
		artAreaHeightSplit = (window.barArea.top - window.upperControlArea.top) * (lowerControlAreaHeightPC * upperControlAreaHeightPCmodifier)
		window.upperControlArea.height = window.barArea.top - window.upperControlArea.top - artAreaHeightSplit
	else:
		controlAreaHeightLock = False
		window.upperControlArea.top = window.controlArea.top + window.controlArea.ymod
		albumArtFullHeight = window.albumArtArea.top + window.albumArtArea.height 
		controlAreaRatio = (albumArtFullHeight - ((albumArtFullHeight) - window.upperControlArea.top)) / albumArtFullHeight
		print('albumArt:',window.albumArtArea.top + window.albumArtArea.height)
		print('controlAreaRatio:',controlAreaRatio)
		if overlap:
			upperControlAreaHeightPCmodifier = 1 + (controlAreaRatio * 0.4)
		artAreaHeightSplit = (window.barArea.top - window.upperControlArea.top) * (lowerControlAreaHeightPC * upperControlAreaHeightPCmodifier)
		window.upperControlArea.height = window.controlArea.height - artAreaHeightSplit - window.controlArea.ymod

	# lowerControlArea
	window.lowerControlArea.left = window.controlArea.left + generalMargin
	window.lowerControlArea.top = window.upperControlArea.top + window.upperControlArea.height
	window.lowerControlArea.width = window.controlArea.width - (generalMargin * 2)
	window.lowerControlArea.height = artAreaHeightSplit - AlbumArtMargin
	
	verticalOpacityModifier = int(100 - (((window.albumArtArea.height + AlbumArtMargin) - window.upperControlArea.top) / (window.albumArtArea.height + AlbumArtMargin)) * 100)
	print('>>>>>>>>>>>>>>>>>>albumArtOpacity',albumArtOpacity + verticalOpacityModifier)

	# upperControlArea
	window.upperControlArea.left = window.controlArea.left + generalMargin
	window.upperControlArea.width = window.controlArea.width - (generalMargin * 2)

	# controlButtonsArea
	mainControlButtonSize = 80
	lesserControlButtonSize = 60
	controlButtonsInnerMargin = int((mainControlButtonSize - lesserControlButtonSize) / 2)

	window.controlButtonsArea.height = mainControlButtonSize
	controlButtonAreaTopPC = 0.55
	controlButtonAreaTopModifier = 1 - (controlAreaRatio * 0.15)
	window.controlButtonsArea.top = window.upperControlArea.top + int(window.upperControlArea.height * (controlButtonAreaTopPC * controlButtonAreaTopModifier)) - int(window.controlButtonsArea.height / 2)
	window.controlButtonsArea.width = window.albumArtArea.width

	window.controlButtonsArea.left = window.controlArea.left + int(window.controlArea.width / 2) - (window.controlButtonsArea.width / 2)

	# define control buttons
	# playButtonArea
	window.playButtonArea.left = window.controlButtonsArea.left + int(window.controlButtonsArea.width / 2) - (mainControlButtonSize / 2)
	window.playButtonArea.top = window.controlButtonsArea.top
	window.playButtonArea.width = mainControlButtonSize
	window.playButtonArea.height = mainControlButtonSize

	controlButtonsXmodifier = window.controlButtonsArea.width * 0.1

	# nextButtonArea
	window.nextButtonArea.width = lesserControlButtonSize
	window.nextButtonArea.height = lesserControlButtonSize
	window.nextButtonArea.left = window.controlButtonsArea.left + window.controlButtonsArea.width - (controlButtonsInnerMargin * 2) - window.nextButtonArea.width - controlButtonsXmodifier
	window.nextButtonArea.top = window.controlButtonsArea.top + controlButtonsInnerMargin

	# previousButtonArea
	window.previousButtonArea.width = lesserControlButtonSize
	window.previousButtonArea.height = lesserControlButtonSize
	window.previousButtonArea.left = window.controlButtonsArea.left + (controlButtonsInnerMargin * 2) + controlButtonsXmodifier
	window.previousButtonArea.top = window.controlButtonsArea.top + controlButtonsInnerMargin

	# metadataArea is split into 5 vertical sections
	# uppermost (titleTextArea) is 24% of metedataZone.height
	# all others (albumTextArea, artistTextArea and gaps between them all) are 19% of metadataArea.height

	titleHeightPC = 24
	titleHeightPX = int((window.lowerControlArea.height / 100) * titleHeightPC)
	otherHeightPC = (100 - titleHeightPC) / 4
	otherHeightPX = int((window.lowerControlArea.height / 100) * otherHeightPC)

	# titleTextArea
	window.titleTextArea.left = window.lowerControlArea.left
	window.titleTextArea.top = window.lowerControlArea.top
	window.titleTextArea.width = window.lowerControlArea.width
	window.titleTextArea.height = titleHeightPX

	# albumTextArea
	window.albumTextArea.left = window.lowerControlArea.left
	window.albumTextArea.top = window.lowerControlArea.top + window.lowerControlArea.height - (otherHeightPX * 3)
	window.albumTextArea.width = window.lowerControlArea.width
	window.albumTextArea.height = otherHeightPX

	# artistTextArea
	window.artistTextArea.left = window.lowerControlArea.left
	window.artistTextArea.top = window.lowerControlArea.top + window.lowerControlArea.height - otherHeightPX
	window.artistTextArea.width = window.lowerControlArea.width
	window.artistTextArea.height = otherHeightPX
"""

def resizeMainPanel(event):
	global window

	window.width = mainPanel.winfo_width()
	window.height = mainPanel.winfo_height()

	zones(window)

	windowCanvas.config(width=window.width, height=window.height)

	windowCanvas.coords(backgroundRectangle,window.left, window.top, window.width, window.height)

	windowCanvas.coords(barAreaRectangle, window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height)

	windowCanvas.coords(artAreaRectangle, window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height)
	
	windowCanvas.coords(albumArtAreaRectangle, window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height)

	windowCanvas.coords(controlAreaRectangle, window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height)

	"""
	windowCanvas.coords(controlButtonsAreaRectangle, window.controlButtonsArea.left, window.controlButtonsArea.top, window.controlButtonsArea.left + window.controlButtonsArea.width, window.controlButtonsArea.top + window.controlButtonsArea.height)

	windowCanvas.coords(playButtonAreaRectangle, window.playButtonArea.left, window.playButtonArea.top, window.playButtonArea.left + window.playButtonArea.width, window.playButtonArea.top + window.playButtonArea.height)
	windowCanvas.coords(nextButtonAreaRectangle, window.nextButtonArea.left, window.nextButtonArea.top, window.nextButtonArea.left + window.nextButtonArea.width, window.nextButtonArea.top + window.nextButtonArea.height)
	windowCanvas.coords(previousButtonAreaRectangle, window.previousButtonArea.left, window.previousButtonArea.top, window.previousButtonArea.left + window.previousButtonArea.width, window.previousButtonArea.top + window.previousButtonArea.height)

	windowCanvas.coords(metadataAreaRectangle, window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height)
	"""
	
	windowCanvas.coords(titleTextAreaRectangle, window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height)
	windowCanvas.coords(albumTextAreaRectangle, window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height)
	windowCanvas.coords(artistTextAreaRectangle, window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height)

	"""
	windowCanvas.coords(lowerControlAreaRectangle, window.lowerControlArea.left, window.lowerControlArea.top, window.lowerControlArea.left + window.lowerControlArea.width, window.lowerControlArea.top + window.lowerControlArea.height)
	windowCanvas.coords(upperControlAreaRectangle, window.upperControlArea.left, window.upperControlArea.top, window.upperControlArea.left + window.upperControlArea.width, window.upperControlArea.top + window.upperControlArea.height)
	"""

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
"""
print('window.albumArtArea: ', window.albumArtArea.top, window.albumArtArea.left, window.albumArtArea.width, window.albumArtArea.height)
"""

# init mainPanel
mainPanel = Tk()

"""
playButtonPNG = Image.open("png/play_button.png")
playButtonImage = ImageTk.PhotoImage(playButtonPNG)

forwardButtonPNG = Image.open("png/forward_button.png")
forwardButtonImage = forwardButtonPNG

backButtonPNG = Image.open("png/back_button.png")
backButtonImage = backButtonPNG
"""

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
controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="yellow")
# controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="#222222")

# albumArtArea rectangle
albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0, fill="green")
# albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0)

"""
# window.lowerControlArea.left rectangle
# lowerControlAreaRectangle = windowCanvas.create_rectangle(window.lowerControlArea.left, window.lowerControlArea.top, window.lowerControlArea.left + window.lowerControlArea.width, window.lowerControlArea.top + window.lowerControlArea.height, width=0, fill="#442200")
lowerControlAreaRectangle = windowCanvas.create_rectangle(window.lowerControlArea.left, window.lowerControlArea.top, window.lowerControlArea.left + window.lowerControlArea.width, window.lowerControlArea.top + window.lowerControlArea.height, width=0)

# window.upperControlArea.left rectangle
# upperControlAreaRectangle = windowCanvas.create_rectangle(window.upperControlArea.left, window.upperControlArea.top, window.upperControlArea.left + window.upperControlArea.width, window.upperControlArea.top + window.upperControlArea.height, width=0, fill="#663300")
upperControlAreaRectangle = windowCanvas.create_rectangle(window.upperControlArea.left, window.upperControlArea.top, window.upperControlArea.left + window.upperControlArea.width, window.upperControlArea.top + window.upperControlArea.height, width=0)

# controlButtonsArea rectangle
# controlButtonsAreaRectangle = windowCanvas.create_rectangle(window.controlButtonsArea.left, window.controlButtonsArea.top, window.controlButtonsArea.left + window.controlButtonsArea.width, window.controlButtonsArea.top + window.controlButtonsArea.height, width=0, fill="gray")
controlButtonsAreaRectangle = windowCanvas.create_rectangle(window.controlButtonsArea.left, window.controlButtonsArea.top, window.controlButtonsArea.left + window.controlButtonsArea.width, window.controlButtonsArea.top + window.controlButtonsArea.height, width=0)

# playButtonArea
playButtonAreaRectangle = windowCanvas.create_rectangle(window.playButtonArea.left, window.playButtonArea.top, window.playButtonArea.left + window.playButtonArea.width, window.playButtonArea.top + window.playButtonArea.height, width=0, fill="grey")

# nextButtonArea
nextButtonAreaRectangle = windowCanvas.create_rectangle(window.nextButtonArea.left, window.nextButtonArea.top, window.nextButtonArea.left + window.nextButtonArea.width, window.nextButtonArea.top + window.nextButtonArea.height, width=0, fill="grey")

# previousButtonArea
previousButtonAreaRectangle = windowCanvas.create_rectangle(window.previousButtonArea.left, window.previousButtonArea.top, window.previousButtonArea.left + window.previousButtonArea.width, window.previousButtonArea.top + window.previousButtonArea.height, width=0, fill="grey")

# metadataArea rectangle
# metadataAreaRectangle = windowCanvas.create_rectangle(window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height, width=0, fill="orange")
metadataAreaRectangle = windowCanvas.create_rectangle(window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height, width=0)
"""

# titleTextArea rectangle
titleTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height, width=0, fill="white")

# albumTextArea rectangle
albumTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height, width=0, fill="white")

# artistTextArea rectangle
artistTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height, width=0, fill="white")

mainPanel.bind( "<Configure>", resizeMainPanel)

mainPanel.mainloop()