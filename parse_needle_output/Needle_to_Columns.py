#!/usr/bin/env python
# Kevin Fang, 2017
# Reads text output from Needle and outputs parsed data to a CSV.

import sys, csv, re

# take args from input, read the text file to a buffer and close it
try:
	testfile = sys.argv[1]
	file = open(testfile, 'r')
	buffer = file.read()
	file.close()
except (IndexError, IOError):
	print "Convert a Needle output .txt file to four column CSV"
	print "Usage: python NeedleParser.py <filename.txt>"
	sys.exit(1)

# regex retrieves the titles of the columns for both items
# For example:
# 1: 7659_1_ORF1 --> 7659_1_ORF1
firstTitle = re.search(r'\# 1: (.+)', buffer).group(1)
# 2: ENST00000351698 --> ENST00000351698
secondTitle = re.search(r'\# 2: (.+)', buffer).group(1)
# generalInformation array holds the titles of the columns for use later in the CSV creation
generalInformation = [firstTitle, secondTitle]

output = "" # a string that sequences are appended to.

# generate a dynamic regex using the first and second titles from input to capture the sequence information
lineSearch = re.compile('(%s |%s )(.+)' % (generalInformation[0][:13], generalInformation[1][:13]))

# use regex to search for sequence information.
# This code block removes all the whitespace in the output fle.
for line in buffer.split('\n'):
	#print(line)
	line = line.rstrip()
	if re.search(lineSearch, line):
		output += line + " "
outputLines = output.split()


# split alignment into starts, ends, and sequences
# query and subject information is alternating in these arrays
# for example, sequences might look like this: [query sequence1, sbjct sequence1, query sequence2, sbjct sequence2]
sequences, starts, ends = [], [], [] # arrays that will hold the sequences, beginnings, and ends (although ends is never used)
for i in range(len(outputLines)): # populate the arrays sequences, starts, and ends
	if i % 4 == 2:
		sequences.append(outputLines[i])
	elif i % 4 == 1:
		starts.append(outputLines[i])
	elif i % 4 == 3:
		ends.append(outputLines[i])

newFileName = "%s.csv" % testfile

#write data to csv file
with open(newFileName, "w+") as csvfile:
	# open a csvWriter and write the initial information.
	csvWriter = csv.writer(csvfile, delimiter= ',')
	csvWriter.writerow(["Protein/Nucleotide of %s" % generalInformation[0]] +
		["Protein/Nucleotide of %s" % generalInformation[1]] + ["Position of %s" % generalInformation[0]] +
		["Position of %s" % generalInformation[1]])

	# loop through sequences and add the data to queryData.
	# xrange is used so sequence will increment by two every time to handle the alternating data format (query, sbjct, query, sbjct, etc_)
	for sequence in xrange(0, len(sequences) - 1, 2):
		queryData = [starts[sequence], ends[sequence], sequences[sequence]] # [start, end, sequence]
		sbjctData = [starts[sequence + 1], ends[sequence + 1], sequences[sequence + 1]] # [start, end, sequence]
		# separate counter for each one - when there is an insertion, the counter is not incremented
		counterQuery = 0
		counterSbjct = 0
		# loop through sequences and write the data to a CSV file
		for letter in range(len(sequences[sequence])):
			csvWriter.writerow([queryData[2][letter]] + [sbjctData[2][letter]] +
				[int(queryData[0]) + counterQuery] +
				[int(sbjctData[0]) + counterSbjct])

			# don't increment the counter if the next character is "-" i.e., when there is an insertion.
			try:
				if queryData[2][letter + 1] != '-':
					counterQuery += 1
				if sbjctData[2][letter + 1] != '-':
					counterSbjct += 1
			except IndexError: # happens when at the last character of the sequence. In this case, the counters no longer matter.
				pass
