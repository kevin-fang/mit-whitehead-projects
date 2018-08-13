#!/usr/bin/env python
# Written by Kevin Fang, 2017

import os, sys, re
global folder

def generateFolderName(name):
	return folder + "/" + name


title = """Bioinformatics datasets available on tak
Datasets are accessible by dataset name in /nfs/BaRC_datasets
Each dataset is more thoroughly described in its README file.
Datasets may be freely shared unless described as "Whitehead access only".
Contact BaRC (bioinformatics@wi.mit.edu) if you have any suggestions of other good resources or would like help with downloading or storage of large datasets that may be of general use.

Dataset\tDescription\tSource
"""

try:
	folder = sys.argv[1]
	readme = sys.argv[2]
except IndexError:
	print "Error: invalid folder"
	print "Usage: ./updateReadme.py <folder containing datasets> <readme.txt>"
	sys.exit(1)

# generates a list of subdirectories in the main directory
directories = os.walk(folder).next()[1]
directories = sorted(directories)
# directories contains a list of all the "descriptions"

# 2D list containing all the entries from the existing readme
entries = []

# search readme for currently present dataset, description, and source information and append to entries
try:
	with open(readme, "r+") as toRead:
		# read through readme file and search for dataset information.
		buffer = toRead.read()
		currentData = re.search(r'Dataset\s.+\n((?:.|\n)+)\n', buffer).group(1).split('\n')
		for item in currentData:
			itemList = item.split('\t')
			if len(itemList) != 0:
				entries.append(itemList)
except (IOError, AttributeError):
	pass

# an array containing all the dataset titles
allDatasets = []
for entry in entries:
	allDatasets.append(entry[0])

# an array containing the datasets that are still present in the folder. Is populated in the next for loop
remainingDatasets = []
# remove all datasets not in the folder anymore
for i in range(len(allDatasets)):
	if allDatasets[i] in directories:
		remainingDatasets.append(allDatasets[i])

# uses remainingDatasets to delete the no longer present entries
remainingEntries = []
for i in range(len(entries)):
	if entries[i][0] in remainingDatasets:
		remainingEntries.append(entries[i])
entries = remainingEntries

# array containing all the directory titles not present in the readme
newDirectories = []
# remove all items in directories that are in datasets - so we don't add duplicates later.
for i in range(len(directories)):
	if directories[i] not in remainingDatasets and directories[i][0] != '.':
		newDirectories.append(directories[i])

# add all the new directories to entries and sort entries in alphabetical order
for directory in newDirectories:
	entries.append([directory, ' ', ' '])
entries = sorted(entries, key=lambda entry: entry[0].lower())

# write to readme
with open(readme, "w") as toWrite:
	toWrite.write(title)
	for entry in entries:
		toWrite.write("\t".join(entry) + '\n')
