#!/usr/bin/env python
# Written by Kevin Fang, 2017
# Description: Converts attribute field of GTF file into tab-delimited format, cutting out attributes without 'gene' and deleting duplicate lines

import re, sys, csv, os

# open files supplied in the arguments
try:
    gtfFile = sys.argv[1]
    outputFile = sys.argv[2]
    gtf = open(gtfFile, "r")
except:
    print "Description: Converts attribute field of GTF file into tab-delimited format, cutting out attributes without 'gene' and deleting duplicate lines"
    print "Usage: ./parse.py <filename.gtf> <output>"
    print "Error: invalid arguments"
    sys.exit(1)

#open the csvfile
with open(outputFile + "temp", "w+") as csvFile:
    # create a tab-delimited "csv" writer
    csvWriter = csv.writer(csvFile, delimiter = '\t')
    csvWriter.writerow(["gene_id"] + ["gene_version"] + ["havana_gene"] +
        ["havana_gene_version"] + ["gene_name"] + ["gene_biotype"] +
        ["gene_source"])
    #scan thorugh each line of the gtf file
    for line in gtf:
        # split each line into the 9 lines and set line to the last.
        line = line.split('\t')[8]
        # regex that captures each name that contains "gene" and its corresponding data in another group
        matches = re.finditer(r'(\S*gene\S*) \"(\S+)\"', line)
        toWrite = {"gene_biotype": "", "gene_id": "", "gene_name": "",
            "gene_source:": "", "gene_version": "", "havana_gene": "", "havana_gene_version": ""}
        # add this data to a dictionary titled "toWrite"
        for match in matches:
            toWrite[match.group(1).rstrip()] = match.group(2).rstrip()

        #writeso" CSV file to row.
        csvWriter.writerow([toWrite["gene_id"], toWrite["gene_version"], toWrite["havana_gene"],
            toWrite["havana_gene_version"], toWrite["gene_name"], toWrite["gene_biotype"],
            toWrite["gene_source"]])

os.system("awk '!seen[$0]++' %s > %s" % (outputFile + "temp", outputFile))
os.system("rm %s" % outputFile + "temp")
