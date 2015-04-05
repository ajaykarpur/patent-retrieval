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

dictionary = {}
doc_lengths = pickle.load(open("doc_lengths.txt", 'r'))
k = pickle.load(open("k.txt", 'r'))
stopwords = pickle.load(open("stopwords.txt", 'r'))

def most_relevant(scores, n):
    # sorted_docs = sorted(sorted(scores), key=scores.get, reverse = True)
    # return sorted_docs[:n]
    heap = heapq.nlargest(n, sorted(scores), key=scores.get)
    return heap

class Query(object):
    def __init__(self, query_string, dictionary):
        self.terms = Counter()
        self.weights = defaultdict(float)
        self.normalized = defaultdict(float)
        self.dictionary = dictionary

        self._tokenize(query_string)
        self._compute_weights()
        self.magnitude = math.sqrt(sum(map(lambda x: x**2, self.weights.values())))
        self._compute_normalized()

    def _tokenize(self, query_string):
        """
        split query into tokens to process
        """
        tokens = [word for sent in nltk.sent_tokenize(query_string) for word in nltk.word_tokenize(sent)]
        tokens = [token.replace('dlr', 'dollar') for token in tokens]
        for token in tokens:
            if token not in stopwords:
                word = stemmer.stem(token).lower()
                self.terms[word] += 1

    def _compute_weights(self):
        """
        compute weights using tf-idf
        """
        for term, count in self.terms.iteritems():
            tf = 1 + math.log(count, 10)
            try:
                df = self.dictionary[term][0]
                idf = math.log(k / df, 10)
            except KeyError:
                idf = 0
            self.weights[term] = tf*idf

    def _compute_normalized(self):
        for term in self.terms:
            try:
                self.normalized[term] = self.weights[term]/self.magnitude
            except ZeroDivisionError:
                self.normalized[term] = 0

    def __len__(self):
        return self.magnitude

def process_queries():

    """
    goes through each line of the query file building
    a post index queue for the queries and then performing that query
    """
    with open(dict_filename, 'r') as d:
        dictionary = pickle.load(d)

    with open(queries_filename,'r') as q, open(post_filename,'r') as p, open(output_filename, 'w') as o:
        
        for line in q: # iterate through each query
            query = Query(line, dictionary)
            # scores = []
            scores = defaultdict(float)
            doc_normalized = defaultdict(float)

            for term in query.terms:
                try:
                    p.seek(dictionary[term][1])
                    posting = pickle.load(p)
                except KeyError:
                    posting = Counter()

                for document in posting:                    
                    doc_normalized[term] = (1 + math.log(posting[document], 10))/doc_lengths[document]
                    product = doc_normalized[term]*query.normalized[term]
                    scores[int(document)] += product

                    # if len(scores) < 10:
                    #     heapq.heappush(scores, (product, -int(document)))
                    # elif product > scores[0]:
                    #     heapq.heapreplace(scores, (product, -int(document)))

            # top_results = [str(-int(i[1])) for i in scores]
            # o.write(" ".join(top_results) + "\n")

            o.write(" ".join(str(x) for x in most_relevant(scores, 10)) + "\n")

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