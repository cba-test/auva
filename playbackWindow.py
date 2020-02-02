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

bar does not resize to better fit very tall, narrow layouts - fixed using ratio of window.width and window.height (window.ratio)
--> control buttons vertical positioning does not modify to fit transition between portrait and landscape
--> meta areas appear to remain squished after vertical size is reduced

text handling - titleText is not moving, font size needs to be calculated to fit controlArea.titleTextArea.height - fixed

SQUISH
squish happens when controlArea.left <= 0
this means the layout is transitioning to portrait mode
this means several things are happened in sequence
art.top decreases (moves up) until art.top <= window.margin
the controlArea is moving down rapidly until controlArea.top >= art.top + art.height

two further things need to happen
art.height decreases until art.top + art.height = predefined split ratio
barArea.height decreases until it reaches predefined modified ratio
--> control area element mids/heights adjust to fit

all of these calculations need to happen in the correct order or they may interact unfavourably

--> put albumArtImage in correct place and ensure it fits

background image considerations
actual size should be slightly larger than window size to prevent blur 'blank border' effect. once blurred, image can be cropped to fit
aspect ratio should be kept to original artwork and final (blurred/cropped) image centred on page
need to use fastest blur -blur 'accuracy' is secondary
"""

from tkinter import *
from tkinter import font

from PIL import Image, ImageFilter, ImageTk, ImageEnhance

global window
global currentState

class currentStateClass:
	isPlaying = False
	currentPlaylist = [] # list of track types
	currentTrack = ''
	mode = 'playback'
	currentTrackPosition = ''

class trackType():
	# title - title of current track
	# album - title of original album
	# artist - artist of current track
	# trackNumber - trackNumber of current track in original album
	# art - image object for album art
	# artFile - direct file location for artwork
	# url - url link for stream
	# bookmarkTrackPosition - saved track position for use with audiobooks
	# isAudiobook - if true, use bookmarkTrackPosition by default

	def __init__(self, title, album, artist, trackNumber, art, artFile, url, bookmarkTrackPosition, isAudiobook):
		self.title = title
		self.album = album
		self.artist = artist
		self.trackNumber = trackNumber
		self.art = art
		self.artFile = artFile
		self.url = url
		self.bookmarkTrackPosition = bookmarkTrackPosition
		self.isAudiobook = isAudiobook

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
	portraitArtSplitRatio = 0.565

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
	splitRatio = 0.65 # 65% of artArea height (this needs to reduce for portrait mode)
	splitRatioMin = 0.45

	portraitModifier = 1

	buttonsMidRatio = 0.68 
	buttonsMidRatioMin = 0.55
	buttonsAreaWidthMin = 440
	buttonsAreaWidthMax = 500
	buttonsAreaMid = 0
	# all MidRatio values are arbitrary
	titleMidRatio = 0.82
	albumMidRatio = 0.53
	artistMidRatio = 0.27
	textHeightModifier = 1
	textHeightModifierMin = 0.8
	textOverlapModifier = 10 # measured in pixels

	largeButtonSize = 60
	smallButtonSize = 45
	
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
		self.textHeightModifier = ((self.textHeightModifier - self.textHeightModifierMin) * self.portraitModifier) + self.textHeightModifierMin

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
		self.split = int(self.height * (((self.splitRatio - self.splitRatioMin) * self.portraitModifier) + self.splitRatioMin))

	def setButtonsMid(self):
		midRatio = ((self.buttonsMidRatio - self.buttonsMidRatioMin) * self.portraitModifier) + self.buttonsMidRatioMin
		self.buttonsAreaMid = self.top + int((self.split - self.top) * midRatio)
		print('setButtonsMid - midRatio',midRatio,self.top,self.buttonsAreaMid)
		
		self.playButtonArea.ymid = self.buttonsAreaMid
		self.nextButtonArea.ymid = self.buttonsAreaMid
		self.previousButtonArea.ymid = self.buttonsAreaMid

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

		midRatio = ((self.buttonsMidRatio - self.buttonsMidRatioMin) * self.portraitModifier) + self.buttonsMidRatioMin
		self.buttonsAreaMid = self.top + int(self.split * midRatio)
		print('setButtonsPositions - midRatio',midRatio,self.top,self.split,self.buttonsAreaMid)

		buttonsAreaLeft = self.left + int(self.width / 2) - (buttonsAreaWidth / 2)

		controlButtonsInnerMargin = int((self.largeButtonSize - self.smallButtonSize) / 2)
		controlButtonsXmodifier = buttonsAreaWidth * 0.1

		# playButtonArea
		self.playButtonArea.width = self.largeButtonSize
		self.playButtonArea.height = self.largeButtonSize
		self.playButtonArea.left = buttonsAreaLeft + int(buttonsAreaWidth / 2) - (self.largeButtonSize / 2)
		self.playButtonArea.ymid = self.buttonsAreaMid
		self.playButtonArea.top_from_mid()

		# nextButtonArea
		self.nextButtonArea.width = self.smallButtonSize
		self.nextButtonArea.height = self.smallButtonSize
		self.nextButtonArea.left = buttonsAreaLeft + buttonsAreaWidth - (controlButtonsInnerMargin * 2) - self.nextButtonArea.width - controlButtonsXmodifier
		self.nextButtonArea.ymid = self.buttonsAreaMid
		self.nextButtonArea.top_from_mid()

		# previousButtonArea
		self.previousButtonArea.width = self.smallButtonSize
		self.previousButtonArea.height = self.smallButtonSize
		self.previousButtonArea.left = buttonsAreaLeft + (controlButtonsInnerMargin * 2) + controlButtonsXmodifier
		self.previousButtonArea.ymid = self.buttonsAreaMid
		self.previousButtonArea.top_from_mid()

	def setMetaMids(self):
		self.titleTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.titleMidRatio)
		self.albumTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.albumMidRatio)
		self.artistTextArea.ymid = (self.top + self.height) - int((self.height - self.split) * self.artistMidRatio)

		self.titleTextArea.top_from_mid()
		self.albumTextArea.top_from_mid()
		self.artistTextArea.top_from_mid()

	def setMetaWidth(self, margin):
		self.titleTextArea.left = self.left + (margin * 1.5) 
		self.titleTextArea.width = self.width - (margin * 3)

		self.albumTextArea.left = self.left + (margin * 1.5)
		self.albumTextArea.width = self.width - (margin * 3)

		self.artistTextArea.left = self.left + (margin * 1.5)
		self.artistTextArea.width = self.width - (margin * 3)

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

	# declare images
	backgroundAreaJPG = ''
	backgroundAreaImage = ''

	playButtonPNG = ''
	playButtonImage = ''

	forwardButtonPNG = ''
	forwardButtonImage = ''

	backButtonPNG = ''
	backButtonImage = ''

	albumArtJPG = ''
	albumArtSized = ''
	albumArtImage = ''

	barAreaJPG = ''
	barAreaImage = ''

	currentTrack = ''

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

				self.controlArea.portraitModifier = 1 - (self.artArea.artOpacity / 100)
			else:
				self.transitionSquish = False

				self.controlArea.portraitModifier = 1
		else:
			# NO OVERLAP - controlArea and artArea are adjoined but seperate
			self.overlap = False
			self.artArea.artOpacity = 100

		self.controlArea.height = self.barArea.top - self.controlArea.top
		self.controlArea.setSplit()

	def init_images(self):
		self.backgroundAreaJPG = Image.open("art/gunship.jpg").resize((window.width, window.height), Image.ANTIALIAS)
		self.backgroundAreaImage = ImageTk.PhotoImage(self.backgroundAreaJPG)

		self.playButtonPNG = Image.open("art/play_button.png").resize((window.controlArea.playButtonArea.width, window.controlArea.playButtonArea.height), Image.ANTIALIAS)
		self.playButtonImage = ImageTk.PhotoImage(self.playButtonPNG)

		self.forwardButtonPNG = Image.open("art/forward_button.png").resize((window.controlArea.nextButtonArea.width, window.controlArea.nextButtonArea.height), Image.ANTIALIAS)
		self.forwardButtonImage = ImageTk.PhotoImage(self.forwardButtonPNG)

		self.backButtonPNG = Image.open("art/back_button.png").resize((window.controlArea.previousButtonArea.width, window.controlArea.previousButtonArea.height), Image.ANTIALIAS)
		self.backButtonImage = ImageTk.PhotoImage(self.backButtonPNG)

		self.albumArtSized = Image.open("art/gunship.jpg").resize((window.artArea.art.width, window.artArea.art.height), Image.ANTIALIAS)
		self.albumArtImage = ImageTk.PhotoImage(self.albumArtSized)

		self.barAreaJPG = Image.open("art/bar.jpg").resize((window.barArea.width, window.barArea.height), Image.ANTIALIAS)
		self.barAreaImage = ImageTk.PhotoImage(self.barAreaJPG)

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

	# windowCanvas.coords(backgroundRectangle,window.left, window.top, window.width, window.height)

	window.backgroundAreaJPG = Image.open(currentState.currentTrack.artFile)
	backgroundWidth, backgroundHeight = window.backgroundAreaJPG.size

	if (window.width / backgroundWidth) < (window.height / backgroundHeight):
		backgroundRatio = window.height / backgroundHeight
	else:
		backgroundRatio = window.width / backgroundWidth

	finalBackgroundWidth = int(backgroundWidth * backgroundRatio)
	finalBackgroundHeight = int(backgroundHeight * backgroundRatio)
	print('---')
	print('finalBackground width, height',finalBackgroundWidth,finalBackgroundHeight)
	print('window width, height',window.width,window.height)
	print('backgroundAreaCrop (pre):',window.backgroundAreaJPG.size)

	window.backgroundAreaJPG = window.backgroundAreaJPG.resize((finalBackgroundWidth, finalBackgroundHeight), Image.ANTIALIAS)

	print('backgroundAreaCrop (resize):',window.backgroundAreaJPG.size)

	if finalBackgroundWidth > window.width:
		modLeft = int((finalBackgroundWidth - window.width) / 2)
		modRight = finalBackgroundHeight - modLeft
		window.backgroundAreaJPG = window.backgroundAreaJPG.crop((modLeft, 0, modRight, finalBackgroundHeight))
		print('crop width',int((finalBackgroundWidth - window.width) / 2))

	if finalBackgroundHeight > window.height:
		modTop = int((finalBackgroundHeight - window.height) / 2)
		modBottom = finalBackgroundHeight - modTop
		window.backgroundAreaJPG = window.backgroundAreaJPG.crop((0, modTop, finalBackgroundWidth, modBottom))
		print('crop height',int((finalBackgroundHeight - window.height) / 2))

	print('backgroundAreaCrop (post):',window.backgroundAreaJPG.size)

	blurredBackgroundAreaImage = window.backgroundAreaJPG.filter(ImageFilter.BoxBlur(20))
	blurredDarkenedBackgroundAreaImage = ImageEnhance.Brightness(blurredBackgroundAreaImage).enhance(0.4)
	window.backgroundAreaImage = ImageTk.PhotoImage(blurredDarkenedBackgroundAreaImage)
	windowCanvas.coords(backgroundImage, window.left, window.top)
	windowCanvas.itemconfig(backgroundImage, image=window.backgroundAreaImage)

	# windowCanvas.coords(barAreaRectangle, window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height)
	# windowCanvas.coords(artAreaRectangle, window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height)
	# windowCanvas.coords(controlAreaRectangle, window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height)

	# windowCanvas.coords(albumArtAreaRectangle, window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height)

	# windowCanvas.coords(playButtonAreaRectangle, window.controlArea.playButtonArea.left, window.controlArea.playButtonArea.top, window.controlArea.playButtonArea.left + window.controlArea.playButtonArea.width, window.controlArea.playButtonArea.top + window.controlArea.playButtonArea.height)
	# windowCanvas.coords(nextButtonAreaRectangle, window.controlArea.nextButtonArea.left, window.controlArea.nextButtonArea.top, window.controlArea.nextButtonArea.left + window.controlArea.nextButtonArea.width, window.controlArea.nextButtonArea.top + window.controlArea.nextButtonArea.height)
	# windowCanvas.coords(previousButtonAreaRectangle, window.controlArea.previousButtonArea.left, window.controlArea.previousButtonArea.top, window.controlArea.previousButtonArea.left + window.controlArea.previousButtonArea.width, window.controlArea.previousButtonArea.top + window.controlArea.previousButtonArea.height)
	
	window.barAreaJPG = Image.open("art/bar.jpg").resize((window.barArea.width, window.barArea.height), Image.ANTIALIAS)
	window.barAreaJPG.putalpha(153) # roughly 60%
	window.barAreaImage = ImageTk.PhotoImage(window.barAreaJPG)
	windowCanvas.coords(barImage, window.barArea.left, window.barArea.top)
	windowCanvas.itemconfig(barImage, image=window.barAreaImage)

	window.albumArtSized = Image.open("art/gunship.jpg")
	window.albumArtSized = window.albumArtSized.resize((int(window.artArea.art.width), int(window.artArea.art.height)), Image.ANTIALIAS)
	window.albumArtSized.putalpha(int(window.artArea.artOpacity * 2.55))
	window.albumArtImage = ImageTk.PhotoImage(window.albumArtSized)
	windowCanvas.coords(artImage, window.artArea.art.left, window.artArea.art.top)
	windowCanvas.itemconfig(artImage, image=window.albumArtImage)

	# windowCanvas.coords(titleTextAreaRectangle, window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height)
	# windowCanvas.coords(albumTextAreaRectangle, window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height)
	# windowCanvas.coords(artistTextAreaRectangle, window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height)

	windowCanvas.coords(playButtonAreaImage, window.controlArea.playButtonArea.left + int(window.controlArea.playButtonArea.width / 2), window.controlArea.playButtonArea.top + int(window.controlArea.playButtonArea.height / 2))
	windowCanvas.coords(nextButtonAreaImage, window.controlArea.nextButtonArea.left + int(window.controlArea.nextButtonArea.width / 2), window.controlArea.nextButtonArea.top + int(window.controlArea.nextButtonArea.height / 2))
	windowCanvas.coords(previousButtonAreaImage, window.controlArea.previousButtonArea.left + int(window.controlArea.previousButtonArea.width / 2), window.controlArea.previousButtonArea.top + int(window.controlArea.previousButtonArea.height / 2))

	windowCanvas.coords(titleText, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top)
	windowCanvas.coords(albumText, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top)
	windowCanvas.coords(artistText, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top)

	titleFont['size'] = -window.controlArea.titleTextArea.height
	albumFont['size'] = -window.controlArea.albumTextArea.height
	artistFont['size'] = -window.controlArea.artistTextArea.height

	windowCanvas.update

def createDarkAllDayAlbum(album):
	album.append(trackType('Woken Furies', 'Dark All Day', 'Gunship', 1, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Dark All Day', 'Dark All Day', 'Gunship', 2, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('When You Grow Up, Your Heart Dies', 'Dark All Day', 'Gunship', 3, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('The Drone Racing League', 'Dark All Day', 'Gunship', 4, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Rise the Midnight Girl', 'Dark All Day', 'Gunship', 5, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Thrasher', 'Dark All Day', 'Gunship', 6, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Black Blood Red Kiss', 'Dark All Day', 'Gunship', 7, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Time After Time', 'Dark All Day', 'Gunship', 8, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Honour Among Thieves', 'Dark All Day', 'Gunship', 9, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Art3mis & Parzival', 'Dark All Day', 'Gunship', 10, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Symmetrical', 'Dark All Day', 'Gunship', 11, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('Cyber City', 'Dark All Day', 'Gunship', 12, '', 'art/gunship.jpg', '', '', False))
	album.append(trackType('The Gates of Disorder', 'Dark All Day', 'Gunship', 13, '', 'art/gunship.jpg', '', '', False))

	for i in range(len(album)):
		print(album[i].trackNumber,'-',album[i].title)

def nextTrack(self):
	# ensure not of last track
	print('=== NEXT TRACK ===')

	nextTrackIndex = currentState.currentPlaylist.index(currentState.currentTrack) + 1
	if nextTrackIndex >= len(currentState.currentPlaylist):
		print('--- END OF PLAYLIST ---')
	else:
		nextTrack = currentState.currentPlaylist[nextTrackIndex]
		print(str(nextTrack.title))
		currentState.currentTrack = nextTrack
		windowCanvas.itemconfigure(titleText, text=currentState.currentTrack.title)

def previousTrack(self):
	# if more than 5 seconds into track OR on first track, move to beginning of current track
	# else move to previous track
	print('=== PREVIOUS TRACK ===')

	previousTrackIndex = currentState.currentPlaylist.index(currentState.currentTrack) - 1
	if previousTrackIndex < 0:
		print('--- BEGINNING OF PLAYLIST ---')
	else:
		previousTrack = currentState.currentPlaylist[previousTrackIndex]
		print(str(previousTrack.title))
		currentState.currentTrack = previousTrack
		windowCanvas.itemconfigure(titleText, text=currentState.currentTrack.title)

# create Dark All Day album metadata
currentState = currentStateClass()
createDarkAllDayAlbum(currentState.currentPlaylist)
currentState.currentTrack = currentState.currentPlaylist[9]

print('Current Track --->',currentState.currentTrack.title)

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

mainPanel.title('Auva')
mainPanel.minsize(480, 480)
mainPanelGeometry = str(window.width) + 'x' + str(window.height)
mainPanel.geometry(mainPanelGeometry)
# mainPanel.resizable(False, False)
# mainPanel.attributes("-topmost", True)

window.init_images()

windowCanvas = Canvas(mainPanel, width = window.width, height = window.height, bd=0, highlightthickness=0)
windowCanvas.pack()

# background rectangle
# backgroundRectangle = windowCanvas.create_rectangle(window.left, window.top, window.width, window.height, width=0, fill="#222222")
backgroundImage = windowCanvas.create_image(window.left, window.top, image = window.backgroundAreaImage, anchor = 'nw')

# barArea rectangle
# barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="blue")
# barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="#111111")
barImage = windowCanvas.create_image(window.barArea.left, window.barArea.top, image = window.barAreaImage, anchor = 'nw')

# artArea rectangle
# artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="red")
# artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="#222222")

# controlArea rectangle
# controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="green")
# controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="#222222")

# albumArtArea rectangle
# albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0, fill="yellow")
# albumArtAreaRectangle = windowCanvas.create_rectangle(window.artArea.art.left, window.artArea.art.top, window.artArea.art.left + window.artArea.art.width, window.artArea.art.top + window.artArea.art.height, width=0)
# create new image using albumArtImage but resized to correctly fit artArea.art
# this requires a comparison between the height & width of both the albumArtImage and artArea
artImage = windowCanvas.create_image(window.artArea.art.left, window.artArea.art.top, image = window.albumArtImage, anchor = 'nw')

# playButtonArea
# playButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.playButtonArea.left, window.controlArea.playButtonArea.top, window.controlArea.playButtonArea.left + window.controlArea.playButtonArea.width, window.controlArea.playButtonArea.top + window.controlArea.playButtonArea.height, width=0, fill="grey")
playButtonAreaImage = windowCanvas.create_image(window.controlArea.playButtonArea.left + int(window.controlArea.playButtonArea.width / 2), window.controlArea.playButtonArea.top + int(window.controlArea.playButtonArea.height / 2), image = window.playButtonImage, anchor = 'center')

# nextButtonArea
# nextButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.nextButtonArea.left, window.controlArea.nextButtonArea.top, window.controlArea.nextButtonArea.left + window.controlArea.nextButtonArea.width, window.controlArea.nextButtonArea.top + window.controlArea.nextButtonArea.height, width=0, fill="grey")
nextButtonAreaImage = windowCanvas.create_image(window.controlArea.nextButtonArea.left + int(window.controlArea.nextButtonArea.width / 2), window.controlArea.nextButtonArea.top + int(window.controlArea.nextButtonArea.height / 2), image = window.forwardButtonImage, anchor = 'center')

# previousButtonArea
# previousButtonAreaRectangle = windowCanvas.create_rectangle(window.controlArea.previousButtonArea.left, window.controlArea.previousButtonArea.top, window.controlArea.previousButtonArea.left + window.controlArea.previousButtonArea.width, window.controlArea.previousButtonArea.top + window.controlArea.previousButtonArea.height, width=0, fill="grey")
previousButtonAreaImage = windowCanvas.create_image(window.controlArea.previousButtonArea.left + int(window.controlArea.previousButtonArea.width / 2), window.controlArea.previousButtonArea.top + int(window.controlArea.previousButtonArea.height / 2), image = window.backButtonImage, anchor = 'center')

# titleTextArea rectangle
# titleTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height, width=0, fill="grey")
# titleTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.titleTextArea.left, window.controlArea.titleTextArea.top, window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top + window.controlArea.titleTextArea.height, width=0)

titleFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.titleTextArea.height, weight="normal")
titleText = windowCanvas.create_text(window.controlArea.titleTextArea.left + window.controlArea.titleTextArea.width, window.controlArea.titleTextArea.top, anchor='ne', justify='right', text=currentState.currentTrack.title, font=titleFont, fill='white')

# albumTextArea rectangle
# albumTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height, width=0, fill="grey")
# albumTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.albumTextArea.left, window.controlArea.albumTextArea.top, window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top + window.controlArea.albumTextArea.height, width=0)

albumFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.albumTextArea.height, weight="normal")
albumText = windowCanvas.create_text(window.controlArea.albumTextArea.left + window.controlArea.albumTextArea.width, window.controlArea.albumTextArea.top, anchor='ne', justify='right', text=currentState.currentTrack.album, font=albumFont, fill='white')

# artistTextArea rectangle
# artistTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height, width=0, fill="grey")
# artistTextAreaRectangle = windowCanvas.create_rectangle(window.controlArea.artistTextArea.left, window.controlArea.artistTextArea.top, window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top + window.controlArea.artistTextArea.height, width=0, fill="black")

artistFont = font.Font(windowCanvas, family="Tw Cen MT", size=-window.controlArea.artistTextArea.height, weight="normal")
artistText = windowCanvas.create_text(window.controlArea.artistTextArea.left + window.controlArea.artistTextArea.width, window.controlArea.artistTextArea.top, anchor='ne', justify='right', text=currentState.currentTrack.artist, font=artistFont, fill='white')

mainPanel.bind("<Configure>", resizeMainPanel)

windowCanvas.tag_bind(nextButtonAreaImage, "<1>", nextTrack)
windowCanvas.tag_bind(previousButtonAreaImage, "<1>", previousTrack)

mainPanel.mainloop()