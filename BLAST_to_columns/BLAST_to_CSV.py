#!/usr/bin/env python
# Kevin Fang, 2017
# Reads text output from BLAST and outputs parsed data to a CSV.

import sys, csv, string, re
global overlapAmount # the amount of HSP alignments

# counters to keep track of the current printing location
global counterQuery
global counterSbjct

# headerBuilder builds a header for the csvWriter - important for when there is more than one matching HSP
def headerBuilder(numTitles):
	argList = []
	for i in range(numTitles):
		argList.extend(["Amino Acid/Nucleotide of Query Seq",
			"Amino Acid/Nucleotide of Subject Seq",
			"Position of Query Seq",
			"Position of Subject Seq",
			""]) # padding is added so there is space between each set of columns
	del argList[-1] # delete padding at the very end
	return argList

# csvLineBuilder build a CSV line containing query data, subject data, query location, and subject location.
# Takes in two 2D arrays containing query/subject data. (allQueryData/allSbjctData)
# letter contains the current location of the letter to be printed
# itemNumber contains the current HSP that is being printed

def csvLineBuilder(allQueryData, allSbjctData, letter, itemNumber):
	global counterQuery
	global counterSbjct
	argList = []
	for i in range(overlapAmount): # works until every HSP is added
		# attempt to add data to the argList - ignore if it is not present.
		try:
			argList.extend([allQueryData[i][itemNumber + 1][letter],
				allSbjctData[i][itemNumber + 1][letter],
				int(allQueryData[i][itemNumber]) + counterQuery[i],
				int(allSbjctData[i][itemNumber]) + counterSbjct[i],
				""])
			try: # checks if the next character is '-', and if so, it will not increment the counters
				if allQueryData[i][itemNumber + 1][letter + 1] != '-':
					counterQuery[i] += 1
				if allSbjctData[i][itemNumber + 1][letter + 1] != '-':
					counterSbjct[i] += 1
			except IndexError: # happens when letter is the last number of the array - ignore.
				pass

		except IndexError:
			argList.extend(["", "", "", "", ""])
	del argList[-1] # delete padding at the end
	return argList

# take text file from input, read the text file and save this data into a buffer
try:
	testfile = sys.argv[1]
	file = open(testfile, 'r')
	buffer = file.read()
	file.close()
except (IndexError, IOError): # print usage if incorrect args are present
	print "Convert a BLAST output .txt file to four column CSV describing HSP\nUsage: python BLAST_to_CSV.py <filename.txt>"
	sys.exit(1)

generalInformation = [] # includes [matched sequence, query] - just general information to be printed

# takes in the sequence producing significant alignment and appends to generalInformation
# For example, if this is in the buffer:
# Sequences producing significant alignments:                       (Bits)  Value
# NP_005359.1  myoglobin [Homo sapiens]                              286     4e-95
#
# generalInformation[0] will be: NP_005359.1
sequence = re.search(r'Sequences.+\n\n(.+)', buffer)
generalInformation.append(sequence.group(1).split()[0])

# cuts out the text between Query and Subj containing the differences
buffer = re.sub(r'(Query.+)\n(.+)(\n.+)', r"\1\3", buffer)
# For example,
# Query  1    MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE  60
#             MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE
# Sbjct  1    MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE  60
# becomes:
# Query  1    MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE  60
# Sbjct  1    MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE  60

# captures all the potential alignments
# ALIGNMENTS
# >NP_005359.1 myoglobin [Homo sapiens]
# SAI82144.1 TPA: globin G [Homo sapiens]
# Length=154
# will returns [NP_005359.1 myoglobin [Homo sapiens], AI82144.1 TPA: globin G [Homo sapiens]]
alignments = re.search(r'ALIGNMENTS\n>((?:.|\n)+)\nLength=', buffer).group(1).split()

# saves all the query data and appends to generalInformation
# Query= protein --> generalInformation[1] becomes 'protein'
query = re.search('Query= (.+)\n+Length=', buffer)
generalInformation.append(query.group(1))

# find every HSP - every match is stored in 'matches', a callable-iterator
matches = re.finditer('(Query (?:\n|.)+?)(?:Score|Database)', buffer)

outputHSP = [] #holds processed data, each sublist contains an aligned HSP
for i in matches:
	outputHSP.append(i.group(1).split())

overlapAmount = len(outputHSP)

newFileName = "%s.csv" % testfile

# used to store data, will become 2-D arrays with width overlapAmount after the alignment splitting in the next line
sequences, starts, ends = [], [], []

# split alignment into starts, ends, and sequences
for hsp in range(overlapAmount):

	# temporary variables that will be eventually added to the 2D array - one for each HSP
	tempSequences = []
	tempStarts = []
	tempEnds = []

	# add information to the HSP to the temporary variables
	for i in range(len(outputHSP[hsp])):
		if i % 4 == 2: # nucleotide/protein values
			tempSequences.append(outputHSP[hsp][i])
		elif i % 4 == 1: # start values
			tempStarts.append(outputHSP[hsp][i])
		elif i % 4 == 3: # end values
			tempEnds.append(outputHSP[hsp][i])

	sequences.append(tempSequences)
	starts.append(tempStarts)
	ends.append(tempEnds)

# write data to csv file
with open(newFileName, "w+") as csvfile:
	# open a csv writer and add in the information from array 'generalInformation' and build a header
	csvWriter = csv.writer(csvfile, delimiter = ',')
	csvWriter.writerow(["Matched Sequence: ", generalInformation[0]] + ["Query: ", generalInformation[1]])
	csvWriter.writerow(["Alignments: ", " ".join(alignments)])
	csvWriter.writerow(headerBuilder(overlapAmount))

	# 2D arrays that hold all the data - each row is a single HSP.
	allQueryData = []
	allSbjctData = []

	#fill the 2D arrays with sbjctData and queryData.
	for hsp in range(overlapAmount):
		queryData = [] # [starts, sequences]
		sbjctData = [] # [starts, sequences]

		# loop thrugh each hsp and add start and sequence data to the query and sbjct data arrays
		for startNum in xrange(0, len(starts[hsp]) - 1, 2):
			queryData.append(starts[hsp][startNum])
			queryData.append(sequences[hsp][startNum])
			sbjctData.append(starts[hsp][startNum + 1])
			sbjctData.append(sequences[hsp][startNum + 1])
		allQueryData.append(queryData)
		allSbjctData.append(sbjctData)

	# the longest sequence - used for iterating through
	maxSeq = max(sequences,key=len)
	# keeps track of which HSP the program is currently printing.
	itemNumber = 0

	# iterate through each sequence and print to CSV.
	for setNum in range(len(maxSeq) / 2):
		# reset counters
		counterQuery = []
		counterSbjct = []

		# need one counter for each HSP
		for i in range(overlapAmount):
			counterQuery.append(0)
			counterSbjct.append(0)

		# maxListinData is used so the program knows how far to iterate into the CSV file.
		# the max(enumerate(...))[0] returns the index of the longest sublist in allQueryData
		maxListinData = max(enumerate(allQueryData), key = lambda tup: len(tup[1]))[0]

		# write the line to the queryData. Will only loop through range as many times as needed
		for letter in range(len(allQueryData[maxListinData][itemNumber + 1])):
			csvWriter.writerow(csvLineBuilder(allQueryData, allSbjctData, letter, itemNumber))
		itemNumber += 2
