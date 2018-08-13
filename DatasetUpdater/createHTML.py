#!/usr/bin/env python
# Written by Kevin Fang, 2017

import os, sys, re
global folder

# generate a folder name for a dataset
def generateFolderName(name):
	return folder + "/" + name

# generates a Tak url from a readme path
def generateTakURL(name):
	# /Volumes/BaRC_datasets/1000_Genomes_PhaseI/README -->
	# http://tak.wi.mit.edu/barc_datasets/1000_Genomes_PhaseI/README
	# the r prefix in front of the regex signifies to search for the raw string i.e., don't treat backslash as an escape character in the string but in the regex instead
	url = re.search(r"BaRC_datasets\/((?:.+))", name).group(1)
	url = "http://tak.wi.mit.edu/barc_datasets/" + url
	return url

# generate a line for the table in the HTML file.
def generateTableLine(dataset, description, source):
	return "<TR><TD><B>%s</TD><TD>%s</TD><TD>%s</TD></TR>\n" % (dataset, description, source)

# generate a line containing a link to a readme for the table in the HTML file.
def generateTableLineWithReadme(readmeUrl, dataset, description, source):
	return '<TR><TD><B><A HREF="%s">%s</A></TD><TD>%s</TD><TD>%s</TD></TR>\n' % (readmeUrl, dataset, description, source)

try:
	folder = sys.argv[1]
	readme = sys.argv[2]
	htmlFile = sys.argv[3] # this will always be the name of the html file
except IndexError:
	print "Error: invalid folder"
	print "Usage: ./updateReadme.py <folder containing datasets> <readme.txt> <htmlfile.html>"
	sys.exit(1)

# populate directories with every subdirectory in the supplied directory and sort
directories = os.walk(folder).next()[1]
tempDirectories = []
for directory in directories:
	if directory[0] != '.':
		tempDirectories.append(directory)

#sort directories - the key=lambda s: s.lower() converts all the strings in directories to lowercase beforehand
directories = sorted(tempDirectories, key=lambda s: s.lower())

allReadme = [] #array that will hold the path to every readme
directoriesWithReadme = [] #array that will hold the directory to every readme

# populates readme arrays
for directory in directories:
	files = []
	try:
		files.extend(os.listdir(generateFolderName(directory)))
	except OSError:
		pass
	for filename in files:
		#print "FILENAME: " + filename
		if filename.lower() == "readme.txt" or filename.lower() == "readme":
			#print directory
			allReadme.append(generateFolderName(directory) + '/' + filename)
			directoriesWithReadme.append(directory)

# generatedURLS contains a sorted list of all the URLS of the README files
# directories contains a list of all the "descriptions"
generatedURLS = []

allReadme = sorted(allReadme, key=lambda s: s.lower())
for item in allReadme:
	generatedURLS.append(generateTakURL(item))

# 2D list containing all the entries from the existing readme
entries = []

# search readme for currently present dataset, description, and source information and append to entries
try:
	with open(readme, "r+") as toRead:
		buffer = toRead.read()
		currentData = re.search(r'Dataset\s.+\n((?:.|\n)+)\n', buffer).group(1).split('\n')
		for item in currentData:
			itemList = item.split('\t')
			if len(itemList) != 0:
				entries.append(itemList)
except (IOError, AttributeError):
	pass


with open(htmlFile, "w") as toWrite:
	#create html file
	toWrite.write("""<HTML>
	<HEAD>
	<TITLE>BaRC datasets on tak</TITLE>
	</HEAD>
	<BODY>

	<H3>Bioinformatics datasets available on tak</H3>

	<H4>Datasets are accessible by dataset name in /nfs/BaRC_datasets<BR>
	Each dataset is more thoroughly described in its README file.<BR>
	Datasets may be freely shared unless described as "Whitehead access only".<BR>
	Contact BaRC (bioinformatics@wi.mit.edu) if you have any suggestions of other good resources or would like help with downloading or storage of large datasets that may be of general use.
	</H4>

	<TABLE BGCOLOR="wheat" BORDER=1>
	<TR BGCOLOR="yellow"><TD><B><B>Dataset</TD><TD><B>Description</TD><TD><B>Source</TD></TR>""")
	counter = 0
	for i in range(len(entries)):
		entry = entries[i]
		# if the length of entry is too short, fill with blank space
		while len(entry) < 3:
			entry.append("")
		# fill HTML file with readme if it is present
		if entry[0] in directoriesWithReadme:
			toWrite.write(generateTableLineWithReadme(generatedURLS[counter], entry[0], entry[1], entry[2]))
			counter += 1
		else:
			toWrite.write(generateTableLine(entry[0], entry[1], entry[2]))

	toWrite.write("""</TD></TR></TABLE>

	</BODY>
	</HTML>
	""")
