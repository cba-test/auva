# -*- coding: utf-8 -*-
"""
AreaRules

@author: cba
"""

from tkinter import *

from PIL import Image, ImageFilter, ImageTk, ImageEnhance

global window

class area:
	top = 0
	left = 0
	width = 0
	height = 0

class playbackWindow:
	top = 0
	left = 0
	width = 0
	height = 0

	# declare main areas
	barArea = area()
	artArea = area()
	controlArea = area()

	# define sub areas
	albumArtArea = area()

	controlButtonsArea = area()

	metadataArea = area()
	titleTextArea = area()
	albumTextArea = area()
	artistTextArea = area()

	playButtonArea = area()
	nextButtonArea = area()
	previousButtonArea = area()

def landscapeZones(window):
	# define main areas
	# barArea
	window.barArea.left = 0
	window.barArea.width = window.width
	window.barArea.height = int(window.height * 0.12) 
	window.barArea.top = window.height - window.barArea.height

	# artArea
	window.artArea.top = 0
	window.artArea.left = 0
	window.artArea.width = int(window.width / 2)
	window.artArea.height = window.barArea.top

	# controlArea
	window.controlArea.top = 0
	window.controlArea.left = window.width - window.artArea.width
	window.controlArea.width = window.artArea.width
	window.controlArea.height = window.barArea.top

	# handle overlap
	# 0.8 is 80%, so the minimum width of controlArea should be 80% of the height of window minus the height of the barArea
	minimumControlWidth = 0.8 * (window.height - window.barArea.height)
	print('minimumControlWidth: ', minimumControlWidth)
	if window.controlArea.width < minimumControlWidth:
		virtualArtArea = window.width - minimumControlWidth
		if virtualArtArea < 0:
			virtualArtArea = 0
		albumArtOpacity = int((virtualArtArea / minimumControlWidth) * 100)
		print('Overlap: ',  albumArtOpacity)
		overlap = True

		window.controlArea.left = window.width - minimumControlWidth
		window.controlArea.width = minimumControlWidth
		if window.controlArea.left < 0:
			# if controlArea has completely overlapped artArea, resize to fit window width properly
			window.controlArea.left = 0
			window.controlArea.width = window.width
	else:
		albumArtOpacity = 100
		print('No Overlap')
		overlap = False

	# set generalMargin
	generalMargin = int(window.artArea.height * 0.04)

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
		window.albumArtArea.top = int((window.artArea.height - window.albumArtArea.width) / 2)

	# controlButtonsArea
	mainControlButtonSize = 100
	lesserControlButtonSize = 80
	controlButtonsInnerMargin = int((mainControlButtonSize - lesserControlButtonSize) / 2)

	window.controlButtonsArea.height = mainControlButtonSize
	window.controlButtonsArea.top = window.controlArea.top + int (window.controlArea.height / 2) - int(window.controlButtonsArea.height / 2)
	window.controlButtonsArea.width = window.controlArea.height - (generalMargin * 2)
	if window.controlButtonsArea.width > (window.controlButtonsArea.height * 7):
		# check overall maximum width
		window.controlButtonsArea.width = window.controlButtonsArea.height * 7
	elif window.controlButtonsArea.width > minimumControlWidth:
		# check overlap sizing fits
		window.controlButtonsArea.width = window.albumArtArea.height
	elif window.controlButtonsArea.width < (window.controlButtonsArea.height * 5):
		# check overall minimum width
		window.controlButtonsArea.width = window.controlButtonsArea.height * 5
	window.controlButtonsArea.left = window.controlArea.left + int(window.controlArea.width / 2) - (window.controlButtonsArea.width / 2)

	print('controlButtonsArea: ', window.controlButtonsArea.width, window.controlButtonsArea.height, minimumControlWidth)

	# define control buttons
	# playButtonArea
	window.playButtonArea.left = window.controlButtonsArea.left + int(window.controlButtonsArea.width / 2) - 50
	window.playButtonArea.top = window.controlButtonsArea.top
	window.playButtonArea.width = mainControlButtonSize
	window.playButtonArea.height = mainControlButtonSize

	# alt method
	# align nextButtonArea.left with window.controlButtonsArea.left + controlButtonsInnerMargin
	# align previous ButtonArea.left with window.controlButtonsArea.left + window.controlButtonsArea.width - controlButtonsInnerMargin - window.previousButtonArea.width
	# apply maximum width algorithm to window.controlButtonsArea.left and window.controlButtonsArea.width

	# nextButtonArea
	window.nextButtonArea.width = lesserControlButtonSize
	window.nextButtonArea.height = lesserControlButtonSize
	window.nextButtonArea.left = window.controlButtonsArea.left + controlButtonsInnerMargin
	window.nextButtonArea.top = window.controlButtonsArea.top + controlButtonsInnerMargin

	# previousButtonArea
	window.previousButtonArea.width = lesserControlButtonSize
	window.previousButtonArea.height = lesserControlButtonSize
	window.previousButtonArea.left = window.controlButtonsArea.left + window.controlButtonsArea.width - controlButtonsInnerMargin - window.previousButtonArea.width
	window.previousButtonArea.top = window.controlButtonsArea.top + controlButtonsInnerMargin


	# titleTextArea, albumTextArea and artistTextArea vertical positioning is relative
	# lower limit is window.controlArea.height - general margin
	# upper limit is window.controlButtonsArea.top + window.controlButtonsArea.height + generalMargin
	
	# metadataArea
	gapBeneathcontrolButtonsArea = (window.barArea.top - generalMargin) - (window.controlButtonsArea.top + window.controlButtonsArea.height)
	window.metadataArea.left = window.controlArea.left + generalMargin
	window.metadataArea.top = window.controlButtonsArea.top + window.controlButtonsArea.height + int(gapBeneathcontrolButtonsArea * 0.4)
	window.metadataArea.width = window.controlArea.width - (generalMargin *2)
	window.metadataArea.height = window.controlArea.height - generalMargin - window.metadataArea.top

	# metadataArea is split into 5 vertical sections
	# uppermost (titleTextArea) is 24% of metedataZone.height
	# all others (albumTextArea, artistTextArea and gaps between them all) are 19% of metadataArea.height

	titleHeightPC = 24
	titleHeightPX = int((window.metadataArea.height / 100) * titleHeightPC)
	otherHeightPC = (100 - titleHeightPC) / 4
	otherHeightPX = int((window.metadataArea.height / 100) * otherHeightPC)

	# titleTextArea
	window.titleTextArea.left = window.metadataArea.left
	window.titleTextArea.top = window.metadataArea.top
	window.titleTextArea.width = window.metadataArea.width
	window.titleTextArea.height = titleHeightPX

	# albumTextArea
	window.albumTextArea.left = window.metadataArea.left
	window.albumTextArea.top = window.metadataArea.top + window.metadataArea.height - (otherHeightPX * 3)
	window.albumTextArea.width = window.metadataArea.width
	window.albumTextArea.height = otherHeightPX

	# artistTextArea
	window.artistTextArea.left = window.metadataArea.left
	window.artistTextArea.top = window.metadataArea.top + window.metadataArea.height - otherHeightPX
	window.artistTextArea.width = window.metadataArea.width
	window.artistTextArea.height = otherHeightPX

def resizeMainPanel(event):
	global window

	window.width = mainPanel.winfo_width()
	window.height = mainPanel.winfo_height()

	landscapeZones(window)

	windowCanvas.config(width=window.width, height=window.height)

	print('Window: ', window.top, window.left, window.width, window.height)

	print('metadataArea top: ', window.metadataArea.top)
	print('metadataArea height: ', window.metadataArea.height)

	windowCanvas.coords(barAreaRectangle, window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height)

	windowCanvas.coords(artAreaRectangle, window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height)
	windowCanvas.coords(albumArtAreaRectangle, window.albumArtArea.left, window.albumArtArea.top, window.albumArtArea.left + window.albumArtArea.width, window.albumArtArea.top + window.albumArtArea.height)

	windowCanvas.coords(controlAreaRectangle, window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height)
	windowCanvas.coords(controlButtonsAreaRectangle, window.controlButtonsArea.left, window.controlButtonsArea.top, window.controlButtonsArea.left + window.controlButtonsArea.width, window.controlButtonsArea.top + window.controlButtonsArea.height)
	windowCanvas.coords(playButtonAreaRectangle, window.playButtonArea.left, window.playButtonArea.top, window.playButtonArea.left + window.playButtonArea.width, window.playButtonArea.top + window.playButtonArea.height)
	windowCanvas.coords(nextButtonAreaRectangle, window.nextButtonArea.left, window.nextButtonArea.top, window.nextButtonArea.left + window.nextButtonArea.width, window.nextButtonArea.top + window.nextButtonArea.height)
	windowCanvas.coords(previousButtonAreaRectangle, window.previousButtonArea.left, window.previousButtonArea.top, window.previousButtonArea.left + window.previousButtonArea.width, window.previousButtonArea.top + window.previousButtonArea.height)

	windowCanvas.coords(metadataAreaRectangle, window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height)
	windowCanvas.coords(titleTextAreaRectangle, window.titleTextArea.left, window.titleTextArea.top, window.titleTextArea.left + window.titleTextArea.width, window.titleTextArea.top + window.titleTextArea.height)
	windowCanvas.coords(albumTextAreaRectangle, window.albumTextArea.left, window.albumTextArea.top, window.albumTextArea.left + window.albumTextArea.width, window.albumTextArea.top + window.albumTextArea.height)
	windowCanvas.coords(artistTextAreaRectangle,window.artistTextArea.left, window.artistTextArea.top, window.artistTextArea.left + window.artistTextArea.width, window.artistTextArea.top + window.artistTextArea.height)

# declare window
window = playbackWindow()

# define window
window.top = 0
window.left = 0
window.width = 1280
window.height = 800

landscapeZones(window)

print('Window: ', window.top, window.left, window.width, window.height)
print('window.barArea: ', window.barArea.top, window.barArea.left, window.barArea.width, window.barArea.height)
print('window.artArea: ', window.artArea.top, window.artArea.left, window.artArea.width, window.artArea.height)
print('window.controlArea: ', window.controlArea.top, window.controlArea.left, window.controlArea.width, window.controlArea.height)
print('window.albumArtArea: ', window.albumArtArea.top, window.albumArtArea.left, window.albumArtArea.width, window.albumArtArea.height)

# init mainPanel
mainPanel = Tk()

mainPanel.title('Auva')
mainPanel.minsize(480, 480)
mainPanelGeometry = str(window.width) + 'x' + str(window.height)
mainPanel.geometry(mainPanelGeometry)
# mainPanel.resizable(False, False)
mainPanel.attributes("-topmost", True)

windowCanvas = Canvas(mainPanel, width = window.width, height = window.height, bd=0, highlightthickness=0)
windowCanvas.pack()

# barArea rectangle
# barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="blue")
barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="#111111")

# artArea rectangle
# artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="red")
artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="#222222")

# controlArea rectangle
# controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="yellow")
controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="#222222")

# albumArtArea rectangle
albumArtAreaRectangle = windowCanvas.create_rectangle(window.albumArtArea.left, window.albumArtArea.top, window.albumArtArea.left + window.albumArtArea.width, window.albumArtArea.top + window.albumArtArea.height, width=0, fill="green")

# controlButtonsArea rectangle
controlButtonsAreaRectangle = windowCanvas.create_rectangle(window.controlButtonsArea.left, window.controlButtonsArea.top, window.controlButtonsArea.left + window.controlButtonsArea.width, window.controlButtonsArea.top + window.controlButtonsArea.height, width=0, fill="gray")

# playButtonArea
playButtonAreaRectangle = windowCanvas.create_rectangle(window.playButtonArea.left, window.playButtonArea.top, window.playButtonArea.left + window.playButtonArea.width, window.playButtonArea.top + window.playButtonArea.height, width=0, fill="white")

# nextButtonArea
nextButtonAreaRectangle = windowCanvas.create_rectangle(window.nextButtonArea.left, window.nextButtonArea.top, window.nextButtonArea.left + window.nextButtonArea.width, window.nextButtonArea.top + window.nextButtonArea.height, width=0, fill="white")

# previousButtonArea
previousButtonAreaRectangle = windowCanvas.create_rectangle(window.previousButtonArea.left, window.previousButtonArea.top, window.previousButtonArea.left + window.previousButtonArea.width, window.previousButtonArea.top + window.previousButtonArea.height, width=0, fill="white")

# metadataArea rectangle
# metadataAreaRectangle = windowCanvas.create_rectangle(window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height, width=0, fill="orange")
metadataAreaRectangle = windowCanvas.create_rectangle(window.metadataArea.left, window.metadataArea.top, window.metadataArea.left + window.metadataArea.width, window.metadataArea.top + window.metadataArea.height, width=0)

# titleTextArea rectangle
titleTextAreaRectangle = windowCanvas.create_rectangle(window.titleTextArea.left, window.titleTextArea.top, window.titleTextArea.left + window.titleTextArea.width, window.titleTextArea.top + window.titleTextArea.height, width=0, fill="white")

# albumTextArea rectangle
albumTextAreaRectangle = windowCanvas.create_rectangle(window.albumTextArea.left, window.albumTextArea.top, window.albumTextArea.left + window.albumTextArea.width, window.albumTextArea.top + window.albumTextArea.height, width=0, fill="white")

# artistTextArea rectangle
artistTextAreaRectangle = windowCanvas.create_rectangle(window.artistTextArea.left, window.artistTextArea.top, window.artistTextArea.left + window.artistTextArea.width, window.artistTextArea.top + window.artistTextArea.height, width=0, fill="white")

mainPanel.bind( "<Configure>", resizeMainPanel)

mainPanel.mainloop()