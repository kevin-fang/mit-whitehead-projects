#!/bin/bash
# Description: Converts attribute field of GTF file into tab-delimited format, cutting out attributes without 'gene' and deleting duplicate lines

./parse.py Homo_sapiens.GRCh38.87.canonical.gtf output.txt
