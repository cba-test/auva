# -*- coding: utf-8 -*-
"""
pillow test

@author: b148.france
"""

from tkinter import *

from PIL import Image, ImageFilter, ImageTk, ImageEnhance

global albumArt, backgroundArt
global imageRatio

mainPanelWidth = 500
mainPanelHeight = 500

def resizeMainPanel(event):
	global albumArt, backgroundArt

	mainPanelWidth = mainPanel.winfo_width()
	mainPanelHeight = mainPanel.winfo_height()
	mainPanelRatio = mainPanelWidth / mainPanelHeight

	# backgroundArt
	imageWidth = mainPanelWidth
	imageHeight = mainPanelHeight
	backgroundArtXOffset = 0
	backgroundArtYOffset = 0

	# fix image ratio
	if mainPanelRatio < imageRatio:
		imageWidth = int(mainPanelHeight * imageRatio)
		backgroundArtXOffset = -int((imageWidth - mainPanelWidth) / 2)

	if mainPanelRatio > imageRatio:
		imageHeight = int(mainPanelWidth * imageRatio)
		backgroundArtYOffset = -int((imageHeight - mainPanelHeight) / 2)

	# still need to apply offset

	print('backgroundArt: ',mainPanelWidth,mainPanelHeight, mainPanelRatio, backgroundArtXOffset, backgroundArtYOffset)

	backgroundArt = backgroundArt.resize((imageWidth, imageHeight))

	blurredAlbumArt = backgroundArt.filter(ImageFilter.GaussianBlur(3))
	blurredDarkenedAlbumArt = ImageEnhance.Brightness(blurredAlbumArt).enhance(0.3)

	backgroundArtImage = ImageTk.PhotoImage(blurredDarkenedAlbumArt)

	backgroundArtLabel.configure(image=backgroundArtImage)
	backgroundArtLabel.image = backgroundArtImage

	# albumArt
	albumArtAreaWidth = int(mainPanelWidth / 2)
	albumArtAreaHeight = int(mainPanelHeight * 0.9)
	albumArtXOffset = 0
	albumArtYOffset = 0

	if albumArtAreaWidth < albumArtAreaHeight:
		albumArtXOffset = int((albumArtAreaHeight - albumArtAreaWidth) / 2)
	elif albumArtAreaWidth > albumArtAreaHeight:
		albumArtYOffset = int((albumArtAreaWidth - albumArtAreaHeight) / 2)

	print('albumArt: ',albumArtAreaWidth,albumArtAreaHeight, albumArtXOffset, albumArtYOffset)
	
	albumArt = albumArt.resize((albumArtAreaWidth, albumArtAreaHeight))
	
	albumArtImage = ImageTk.PhotoImage(albumArt)
	albumArtLabel.configure(image=albumArtImage)
	albumArtLabel.place(x=albumArtXOffset, y=albumArtYOffset)
	albumArtLabel.image = albumArtImage

# init mainPanel
mainPanel = Tk()

mainPanel.title('Auva')
mainPanel.minsize(mainPanelWidth, mainPanelHeight)
mainPanel.geometry('1280x800')
# mainPanel.resizable(False, False)
mainPanel.attributes("-topmost", True)

print('mainPanelWidth: ' + str(mainPanelWidth))
print('mainPanelHeight: ' + str(mainPanelHeight))

albumArt = Image.open("dark_all_day.jpg")
backgroundArt = albumArt

imageWidth, imageHeight = albumArt.size
imageRatio = imageWidth / imageHeight
print('imageWidth: ' + str(imageWidth))
print('imageHeight: ' + str(imageHeight))
print('imageRatio: ' + str(imageRatio))
albumArt = albumArt.resize((mainPanelWidth, mainPanelHeight))

albumArtImage = ImageTk.PhotoImage(albumArt)
backgroundArtImage = ImageTk.PhotoImage(backgroundArt)

"""
blurredAlbumArt = albumArt.filter(ImageFilter.GaussianBlur(3))
blurredDarkenedAlbumArt = ImageEnhance.Brightness(blurredAlbumArt).enhance(0.3)

backgroundArtImage = ImageTk.PhotoImage(blurredDarkenedAlbumArt)
"""

backgroundArtLabel = Label(mainPanel, image=backgroundArtImage, borderwidth=0)
backgroundArtLabel.image = backgroundArtImage
backgroundArtLabel.place(x=0, y=0)

albumArtLabel = Label(mainPanel, image=albumArtImage, borderwidth=0)
albumArtLabel.image = albumArtImage
albumArtLabel.place(x=10, y=10)

resizeMainPanel

# second image required to show clear version of image on top of blurred image

mainPanel.bind( "<Configure>", resizeMainPanel)

mainPanel.mainloop()