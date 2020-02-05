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

def parseLibrary(libraryFolderList):
	for folderPath in libraryFolderList:
		print('folder:', folderPath)

		yield from parseFolder(folderPath)

def parseFolder(folderPath):
	# looks through given folder for more folders and files

	print ('\nscan:',folderPath)
	scan = os.scandir(folderPath)

	for entry in scan:
		if entry.is_dir():
			# print('folderlist',str(entry.path))
			yield from parseFolder(entry.path)

		if entry.is_file():
			# print('parseFile',str(entry.path))
			yield parseFile(entry.path)

def parseFile(filePath):
	# extract header of file into fileData

	print('file:', filePath)

	fileData = filePath.split('\\')[-1]

	fileType = fileData.split('.')[-1]

	if fileType == 'mp3' or fileType == 'flac':
		return fileData
	else:
		return None

def readFileData(fileData):
	# look at fileData to determine what it is
	# always return metaData, but fill key fields with notifiers if metaData is borked

	return metaData

libraryFolderList = []

startFolders(libraryFolderList)

for libraryFolder in libraryFolderList:
	print(str(libraryFolder))

library = parseLibrary(libraryFolderList)

for el in library:
	if el:
		print('---->',str(el))