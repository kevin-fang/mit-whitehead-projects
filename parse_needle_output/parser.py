#!/usr/bin/env python

import csv
import re
import os
import sys

# csvfile = open("sample.gff")
# needleReader = csv.reader(csvfile, delimiter='	')
#get number of aligned sequences
fileToConvert = sys.argv[-1]

if re.search("parser\.py",sys.argv[-1]):
	print "#################################################"
	print "# Usage: python parser.py path/to/input.needle  #"
	print "#################################################"
	sys.exit()

#adds to a `list` of gff features

def setFeature(start, end, oStart, oEnd, diffType, seq1Diffs, seq2Diffs):
	#start = beginning of first sequence, end = etc
	#oSTart = beginning of sencond sequnece, oend = etc
	#diffType = type of difference exhibited
        #goes through, see's what type of difference each difference is, and appends the appropriate note
	global groupNum #so that we don't get local variables
	if diffType == 'seq2Insertion':
		note1 = "Insertion of " + str(len(seq2Diffs)) + " bases in " + sequences[1] + ";replace=" + seq2Diffs
		note2 = "Insertion of " + str(len(seq2Diffs)) + " bases in " + sequences[1] + ";replace="# + seq2Diffs
		seq1Out.append({'seqname':sequences[0], 'source':'needle', 'feature':'sequence_conflict', 'start':str(start), 'end':str(end), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[0] + '.' + str(groupNum) + ';note=' + note1})
		seq2Out.append({'seqname':sequences[1], 'source':'needle', 'feature':'sequence_conflict', 'start':str(oStart), 'end':str(oEnd), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[1] + '.' + str(groupNum) + ';note=' + note2})

	elif diffType == 'seq1Insertion':
		note1 = "Insertion of " + str(len(seq1Diffs)) + " bases in " + sequences[0] + ";replace="
		note2 = "Insertion of " + str(len(seq1Diffs)) + " bases in " + sequences[0] + ";replace=" + seq1Diffs
		seq1Out.append({'seqname':sequences[0], 'source':'needle', 'feature':'sequence_conflict', 'start':str(start), 'end':str(end), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[0] + '.' + str(groupNum) + ';note=' + note1})
		seq2Out.append({'seqname':sequences[1], 'source':'needle', 'feature':'sequence_conflict', 'start':str(oStart), 'end':str(oEnd), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[1] + '.' + str(groupNum) + ';note=' + note2})

	elif diffType == 'SNP':
		note1 = "SNP in " + sequences[1] + ";replace=" + seq2Diffs
		note2 = "SNP in " + sequences[0] + ";replace=" + seq1Diffs
		seq1Out.append({'seqname':sequences[0], 'source':'needle', 'feature':'sequence_conflict', 'start':str(start), 'end':str(end), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[0] + '.' + str(groupNum) + ';note=' + note1})
		seq2Out.append({'seqname':sequences[1], 'source':'needle', 'feature':'sequence_conflict', 'start':str(oStart), 'end':str(oEnd), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[1] + '.' + str(groupNum) + ';note=' + note2})

	elif diffType == 'replace':
                #hold strings for each line for each sequence
		note1 = sequences[1] + ";replace=" + seq2Diffs
		note2 = sequences[0] + ";replace=" + seq1Diffs
                #arrays that hold each set of lines for each sequence
		seq1Out.append({'seqname':sequences[0], 'source':'needle', 'feature':'sequence_conflict', 'start':str(start), 'end':str(end), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[0] + '.' + str(groupNum) + ';note=' + note1})
		seq2Out.append({'seqname':sequences[1], 'source':'needle', 'feature':'sequence_conflict', 'start':str(oStart), 'end':str(oEnd), 'score':'.', 'strand':'+', 'frame':'.', 'group':'ID=' + sequences[1] + '.' + str(groupNum) + ';note=' + note2})

	groupNum = groupNum + 1

sequences = []
getSequences = 0
groupNum = 0
f = open(fileToConvert,'r')
fLines = list(f)
currentIndex = 0
fn1 = ''
fn2 = ''
for line in fLines:
	#whitespace is taken out
        ln = line.rstrip()

	#finds
        if re.search("^#\s\s\s\s-asequence", ln):#ln[:16] == "#    -asequence":
		fn1 = ln[16:]

	if re.search("^#\s\s\s\s-bsequence", ln):#ln[:16] == "#    -asequence":
		fn2 = ln[16:]
        #sees whether the file starts to describe the aligned sequences
	if ln[:21] == "# Aligned_sequences: ":
		getSequences = 1

        #gets sequence names
	elif getSequences == 1:
		if re.search('^# [0-9]: .',ln):
			sequences.append(ln[5:])
		else:
			getSequences = 0;
        #if it finds the bottom thing, it starts into the normal parsing mode
	elif ln[:40] == "#=======================================" and len(sequences) != 0:
		currentIndex = currentIndex + 1
		break;
	currentIndex = currentIndex + 1

seq1Out = [] #{seqname:sequences[0],source:'needle',feature:'sequence_conflict',start:(int),end:(int),score:'.',strand:'+',frame:'.', group:'sequences[] + "len(sequences[0]) + 1"'}

seq2Out = [] #{seqname:sequences[1],source:'needle',feature:'sequence_conflict',start:(int),end:(int),score:'.',strand:'+',frame:'.', group:'sequences[] + "len(sequences[1]) + 1"'}

#total index
counter = 0
#variables to store each subsequence
seq1 = ''
seq2 = ''
#current "real" position in sequence, not counting gaps
seq1Index = 0
seq2Index = 0
parseIndex = 0
difference = [0,None] #whether there is a run of differences right now, type of difference
seq1Differences = [None, None]
seq2Differences = [None, None]
seq1Diff = '' #actual strand that in sequence one that is part of the current difference strand
seq2Diff = '' #actual strand that in sequence two that is part of the current difference strand

fn1 = os.path.splitext(os.path.basename(fn1))[0] + ".gff"
fn2 = os.path.splitext(os.path.basename(fn2))[0] + ".gff"

#goes through rest of file
for line in fLines[currentIndex:]:
	ln = line.rstrip()
	# print str(parseIndex % 4) + " " + ln
    #gets first subsequence
	if parseIndex % 4 == 1:
		seq1 = ln[21:-7]
        #gets second subsequence
	elif parseIndex % 4 == 3:
		seq2 = ln[21:-7]
		# print seq1
		# print seq2
		# print '\n'
		for i in range(len(seq1)):
			if seq1[i] == '-': #if there is an insertion in seq2 or a deletion in seq1
				seq2Index = seq2Index + 1 #add to index of seq2
				if difference[0] == 0: #if there isn't a currently running difference
					difference[0] = 1
					difference[1] = 'seq2Insertion' #set type of difference
					seq1Differences[0] = seq1Index #set the first index of the difference for seq1
					seq2Differences[0] = seq2Index #set the first index of the difference for seq2
					seq2Diff = seq2[i]
				elif difference[1] == 'seq2Insertion':
					seq2Diff = seq2Diff + seq2[i]
				else: # this case never actually happens
					print "DOES THIS EVER EVEN HAPPEN"
					seq1Differences[1] = seq1Index - 1 #should this be -1? Seems like in SNPs it is in the normal gff formats.
					seq2Differences[1] = seq2Index - 1
					setFeature(seq1Differences[0], seq1Differences[1], seq2Differences[0], seq2Differences[1], difference[1], seq1Diff, seq2Diff)
					difference[0] = 0
					difference[1] = None
			elif seq2[i] == '-':
				seq1Index = seq1Index + 1
				if difference[0] == 0: #if there isn't a currently running difference
					difference[1] = 'seq1Insertion' #set type of difference
					difference[0] = 1
					seq2Differences[0] = seq2Index #set the first index of the difference for seq2
					seq1Differences[0] = seq1Index #set the first index of the difference for seq1
					seq1Diff = seq1[i]

				elif difference[1] == 'seq1Insertion':
					seq1Diff = seq1Diff + seq1[i]
				else: #never actually happens
					seq1Differences[1] = seq1Index - 1 #should this be -1? Seems like in SNPs it is in the normal gff formats.
					seq2Differences[1] = seq2Index - 1
					setFeature(seq1Differences[0], seq1Differences[1], seq2Differences[0], seq2Differences[1], difference[1], seq1Diff, seq2Diff)
					difference[0] = 0
					difference[1] = None

			elif seq2[i] != seq1[i]:
				seq1Index += 1
				seq2Index += 1
				if difference[0] == 0: #if there isn't a currently running difference
					difference[1] = 'SNP' #set type of difference
					difference[0] = 1
					seq2Differences[0] = seq2Index #set the first index of the difference for seq2
					seq1Differences[0] = seq1Index #set the first index of the difference for seq1
					seq2Diff = seq2[i]
					seq1Diff = seq1[i]
				elif difference[1] == 'SNP':
						seq2Diff = seq2Diff + seq2[i]
						seq1Diff = seq1Diff + seq1[i]
						difference[1] = 'replace'
				elif difference[1] == 'replace':
					seq2Diff = seq2Diff + seq2[i]
					seq1Diff = seq1Diff + seq1[i]
				else:
					seq1Differences[1] = seq1Index - 1 #should this be -1? Seems like in SNPs it is in the normal gff formats.
					seq2Differences[1] = seq2Index - 1
					setFeature(seq1Differences[0], seq1Differences[1], seq2Differences[0], seq2Differences[1], difference[1], seq1Diff, seq2Diff)
					difference[0] = 0
					difference[1] = None
				#SET / CONTINUE / STOP A DIFFERENCE?
			elif seq2[i] == seq1[i]:
				seq2Index = seq2Index + 1
				seq1Index = seq1Index + 1
				if difference[0] == 1:
					seq1Differences[1] = seq1Index - 1 #should this be -1? Seems like in SNPs it is in the normal gff formats.
					seq2Differences[1] = seq2Index - 1
					setFeature(seq1Differences[0], seq1Differences[1], seq2Differences[0], seq2Differences[1], difference[1], seq1Diff, seq2Diff)
					difference[0] = 0
					difference[1] = None

				#STOP A DIFFERENCE?
	currentIndex = currentIndex + 1
	parseIndex = parseIndex + 1

if difference[0] == 1:
	seq1Differences[1] = seq1Index #should this be -1? Seems like in SNPs it is in the normal gff formats.
	seq2Differences[1] = seq2Index
	setFeature(seq1Differences[0], seq1Differences[1], seq2Differences[0], seq2Differences[1], difference[1], seq1Diff, seq2Diff)

with open(fn1,'w+') as csvfi:
	csvwriter = csv.writer(csvfi, delimiter='	')
	for item in seq1Out:
		csvwriter.writerow([item['seqname'],item['source'],item['feature'],item['start'],item['end'],item['score'],item['strand'],item['frame'],item['group']])

with open(fn2,'w+') as csvfi:
	csvwriter = csv.writer(csvfi, delimiter='	')
	for item in seq2Out:
		csvwriter.writerow([item['seqname'],item['source'],item['feature'],item['start'],item['end'],item['score'],item['strand'],item['frame'],item['group']])
