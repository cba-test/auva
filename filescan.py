# -*- coding: utf-8 -*-
"""
filescan

@author: cba

simple method for scanning folder structures to find file information as quickly as possible
"""

def startFolders(libraryFolderList):
	# creates an initial folder list, allowing the rest of the code to be as close to the final required design as possible

	libraryFolderList.append(r'C:\Users\cafeb\Documents\GitHub\auva\music')

	return libraryFolderList

def parseFolder(folder):
	# looks through given folder for more folders and files

	if numOfFiles > 0:
		# yield parseFile
		return fileData
	else:
		return None

def parseFile(file):
	# extract header of file into fileData

	return fileData

def readFileData(fileData):
	# look at fileData to determine what it is
	# always return metaData, but fill key fields with notifiers if metaData is borked

	return metaData

libraryFolderList = []

startFolders(libraryFolderList)

print(str(libraryFolderList))