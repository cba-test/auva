# -*- coding: utf-8 -*-
"""
filescan

@author: cba

simple method for scanning folder structures to find file information as quickly as possible
"""

import os

def startFolders(libraryFolderList):
	# creates an initial folder list, allowing the rest of the code to be as close to the final required design as possible

	libraryFolderList.append(r'C:\Users\cafeb\Documents\GitHub\auva\music')

	return libraryFolderList

def parseFolder(folderPath):
	# looks through given folder for more folders and files

	print('folder:', folderPath)

	folders = []
	files = []

	for r, d, f in os.walk(folderPath):
		for folder in d:
			folders.append(os.path.join(r, folder))
		for file in f:
			files.append(os.path.join(r, file))

	numOfFolders = len(folders)
	numOfFiles = len(files)

	if numOfFolders > 0
		for folder in folders:
			yield(parseFolder(folder))

	if numOfFiles > 0:
		for file in files:
			yield(parseFile(file))

	return None

def parseFile(filePath):
	# extract header of file into fileData

	print('file:', filePath)

	fileData = filePath.split('\')[-1]

	return fileData

def readFileData(fileData):
	# look at fileData to determine what it is
	# always return metaData, but fill key fields with notifiers if metaData is borked

	return metaData

libraryFolderList = []

startFolders(libraryFolderList)

print(str(libraryFolderList))