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

	controlZone = area()
	titleZone = area()
	albumZone = area()
	artistZone = area()

def landscapeZones(window):
	# define main areas
	window.barArea.left = 0
	window.barArea.width = window.width
	window.barArea.height = int(window.height * 0.12) 
	window.barArea.top = window.height - window.barArea.height

	window.artArea.top = 0
	window.artArea.left = 0
	window.artArea.width = int(window.width / 2)
	window.artArea.height = window.barArea.top

	window.controlArea.top = 0
	window.controlArea.left = window.width - window.artArea.width
	window.controlArea.width = window.artArea.width
	window.controlArea.height = window.barArea.top

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

	generalMargin = int(window.artArea.height * 0.04)

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

	window.controlZone.top = window.controlArea.top + int (window.controlArea.height / 2) - 50 # assuming height of controls is 100
	window.controlZone.width = window.controlArea.width - (generalMargin * 2)
	if window.controlZone.width > window.albumArtArea.width:
		window.controlZone.width = window.albumArtArea.width
	window.controlZone.left = window.width - generalMargin - window.controlZone.width
	window.controlZone.height = 100

def resizeMainPanel(event):
	global window

	window.width = mainPanel.winfo_width()
	window.height = mainPanel.winfo_height()

	landscapeZones(window)

	windowCanvas.config(width=window.width, height=window.height)

	print('Window: ', window.top, window.left, window.width, window.height)

	print('controlArea left: ', window.controlArea.left)

	windowCanvas.coords(barAreaRectangle, window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height)
	windowCanvas.coords(artAreaRectangle, window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height)
	windowCanvas.coords(controlAreaRectangle, window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height)
	windowCanvas.coords(albumArtAreaRectangle, window.albumArtArea.left, window.albumArtArea.top, window.albumArtArea.left + window.albumArtArea.width, window.albumArtArea.top + window.albumArtArea.height)
	windowCanvas.coords(controlZoneRectangle, window.controlZone.left, window.controlZone.top, window.controlZone.left + window.controlZone.width, window.controlZone.top + window.controlZone.height)

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
barAreaRectangle = windowCanvas.create_rectangle(window.barArea.left, window.barArea.top, window.barArea.left + window.barArea.width, window.barArea.top + window.barArea.height, width=0, fill="blue")

# artArea rectangle
artAreaRectangle = windowCanvas.create_rectangle(window.artArea.left, window.artArea.top, window.artArea.left + window.artArea.width, window.artArea.top + window.artArea.height, width=0, fill="red")

# controlArea rectangle
controlAreaRectangle = windowCanvas.create_rectangle(window.controlArea.left, window.controlArea.top, window.controlArea.left + window.controlArea.width, window.controlArea.top + window.controlArea.height, width=0, fill="yellow")

# albumArtArea rectangle
albumArtAreaRectangle = windowCanvas.create_rectangle(window.albumArtArea.left, window.albumArtArea.top, window.albumArtArea.left + window.albumArtArea.width, window.albumArtArea.top + window.albumArtArea.height, width=0, fill="green")

# controlZone rectangle
controlZoneRectangle = windowCanvas.create_rectangle(window.controlZone.left, window.controlZone.top, window.controlZone.left + window.controlZone.width, window.controlZone.top + window.controlZone.height, width=0, fill="white")

mainPanel.bind( "<Configure>", resizeMainPanel)

mainPanel.mainloop()