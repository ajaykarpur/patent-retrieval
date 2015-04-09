#!/usr/bin/python
import sys
import getopt
from collections import defaultdict, Counter
import heapq
import string
import pickle
import math
import nltk
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

#-------------------------------------------------------------------------------

def most_relevant(scores, n):
    heap = heapq.nlargest(n, sorted(scores), key=scores.get)
    return heap

class Query(object):
    def __init__(self, query_string, dictionary):
        

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries_filename -o output-file-of-results"

dict_filename = post_filename = queries_filename = output_filename = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except:
    usage()
    sys.exit(2)
        
for o, a in opts:
    if o == '-d':
        dict_filename = a
    elif o == '-p':
        post_filename = a
    elif o == '-q':
        queries_filename = a
    elif o == '-o':
        output_filename = a
    else:
        assert False, "unhandled option"
if dict_filename == None or post_filename == None or queries_filename == None or output_filename == None:
    usage()
    sys.exit(2)


process_queries()