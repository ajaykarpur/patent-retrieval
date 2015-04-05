#!/usr/bin/python
import sys
import getopt
import os
import string
import pickle
from collections import defaultdict, Counter
import math
import nltk
import re
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

try:
    from lxml import etree
    print("running with lxml.etree")
except ImportError:
    try:
    # Python 2.5+
        import xml.etree.cElementTree as etree
        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
        # Python 2.5+
            import xml.etree.ElementTree as etree
            print("running with ElementTree on Python 2.5+")
        except ImportError:
            print("Failed to import ElementTree from any known place")
            sys.exit()

from lib.gensim.models import lsimodel

#-------------------------------------------------------------------------------

class Indexer(object):
    def __init__(self, doc_directory, dict_filename, post_filename, k):
        self.k = k
        self.dict_filename = dict_filename
        self.post_filename = post_filename

        self.field_weights = {}
        self.postings = defaultdict(Counter)
        self.dictionary = {}
        self.doc_lengths = defaultdict(float)

        # with open("stopwords") as s:
        #     self.stopwords = set(s.read().split())
        # self.stopwords = set(string.punctuation).union(self.stopwords)
        
        # self.create_postings(doc_directory)
        # self.write_files()

        self.set_field_weights()
        self.parse_xml(doc_directory)

    def set_field_weights(self):
        self.field_weights["Patent Number"] =                   1
        self.field_weights["Application Number"] =              1
        self.field_weights["Kind Code"] =                       1
        self.field_weights["Title"] =                           1
        self.field_weights["Document Types"] =                  1
        self.field_weights["Application Date"] =                1
        self.field_weights["Application Year"] =                1
        self.field_weights["Application(Year/Month)"] =         1
        self.field_weights["Publication Date"] =                1
        self.field_weights["Publication Year"] =                1
        self.field_weights["Publication(Year/Month)"] =         1
        self.field_weights["All IPC"] =                         1
        self.field_weights["IPC Primary"] =                     1
        self.field_weights["IPC Section"] =                     1
        self.field_weights["IPC Class"] =                       1
        self.field_weights["IPC Subclass"] =                    1
        self.field_weights["IPC Group"] =                       1
        self.field_weights["Family Members"] =                  1
        self.field_weights["Family Member Count"] =             1
        self.field_weights["Family Members Cited By Count"] =   1
        self.field_weights["Other References"] =                1
        self.field_weights["Other References Count"] =          1
        self.field_weights["Cited By Count"] =                  1
        self.field_weights["Cites"] =                           1
        self.field_weights["Cites Count"] =                     1
        self.field_weights["Priority Country"] =                1
        self.field_weights["Priority Number"] =                 1
        self.field_weights["Priority Date"] =                   1
        self.field_weights["Assignee(s)"] =                     1
        self.field_weights["1st Assignee"] =                    1
        self.field_weights["Number of Assignees"] =             1
        self.field_weights["1st Assignee Address"] =            1
        self.field_weights["Assignee(s) Address"] =             1
        self.field_weights["Inventor(s)"] =                     1
        self.field_weights["1st Inventor"] =                    1
        self.field_weights["Number of Inventors"] =             1
        self.field_weights["1st Inventor Address"] =            1
        self.field_weights["Inventor(s) Address"] =             1
        self.field_weights["Agent/Attorney"] =                  1
        self.field_weights["cited by within 3 years"] =         1
        self.field_weights["cited by within 5 years"] =         1
        
    def parse_xml(self, dirname):

        # def etree_to_dict(t):
        #     d = {t.tag : map(etree_to_dict, t.iterchildren())}
        #     d.update((k, v) for k, v in t.attrib.iteritems())
        #     d['text'] = t.text
        #     return d

        with open("pickled_patent_dicts", 'w') as pickledicts:
            for count, patent_file in enumerate(os.listdir(dirname)):
                patent_num, ext = patent_file.split(".")


                with open(os.path.join(dirname, patent_file)) as f:
                    if count == self.k: # index k documents
                        break

                    fields = {}

                    xml = etree.parse(f)

                    for element in xml.iter():
                        for k, v in element.attrib.iteritems():
                            if k != "doc":
                                attribute = v
                                if attribute != None and element.text != None:
                                    fields[attribute] = element.text.strip().encode("utf-8")
                    pickle.dump(fields, pickledicts)
            
    def create_postings(self, dirname):
        """
        create a dict of words and their associated posting lists with term frequency
        in the format {"word": {"doc_id": tf}}
        eg. {"bill": {"1": 3, "10": 23, "109": 7}}
        """

        def remove_stopwords(): # remove stopwords if given
            if "stopwords" in os.listdir(os.path.dirname(dirname)):
                with open(os.path.join(os.path.dirname(dirname), "stopwords")) as s:
                    self.stopwords = set(s.read().split()).union(self.stopwords)

        def remove_numbers(text):
            return text.translate(None, string.digits)

        remove_stopwords()

        for count, doc_id in enumerate(os.listdir(dirname)):
            weights = defaultdict(float)

            if count == self.k: # use k documents to train
                break

            with open(os.path.join(dirname, doc_id)) as f:
                text = f.read()
                
                # text = remove_numbers(text)
                
                tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
                tokens = map(lambda t: stemmer.stem(t).lower(), tokens)
                for token in tokens:
                    if token not in self.stopwords:
                        self.postings[token][doc_id] += 1

                split_word = re.split('[- /]',token)
                if len(split_word) > 1:
                    for subword in split_word:
                        if subword not in self.stopwords:
                                subword = stemmer.stem(subword).lower()
                                self.postings[subword][doc_id] += 1

                for token in tokens:
                    if token not in self.stopwords:
                        for document in self.postings[token]:
                            weights[token] = (1 + math.log(self.postings[token][document], 10))

            self.doc_lengths[doc_id] = math.sqrt(sum(map(lambda x: x**2, weights.values())))


    def write_files(self):
        """
        write dictionary.txt and posting.txt
        make dictionary {"word": frequency, offset}, where frequency is the size
        of the posting list and offset is the location in postings.txt
        """
        with open(self.post_filename, 'w') as f: # write postings.txt
            for word in self.postings:
                frequency = len(self.postings[word])
                offset = f.tell() # location in the postings.txt file
                self.dictionary[str(word)] = frequency, offset
                
                pickle.dump(self.postings[word], f)

        pickle.dump(self.dictionary, open(self.dict_filename, "wb")) # write dictionary.txt
        pickle.dump(self.doc_lengths, open("doc_lengths.txt"), "wb")
        pickle.dump(self.stopwords, open("stopwords.txt"), "wb")


#-------------------------------------------------------------------------------
# added a new flag to accept values of k (for subsets of k documents)

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-doc_directory -d dict_filename-file -p post_filename-file"

doc_directory = dict_filename = post_filename = k = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:k:')
except:
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
        
for o, a in opts:
    if o == '-i':
        doc_directory = a
    elif o == '-d':
        dict_filename = a
    elif o == '-p':
        post_filename = a
    elif o == '-k':
        k = int(a)
    else:
        assert False, "unhandled option"
if doc_directory == None or dict_filename == None or post_filename == None:
    usage()
    sys.exit(2)
if k == None:
    k = len(os.listdir(doc_directory))

my_index = Indexer(doc_directory, dict_filename, post_filename, k)
# pickle.dump(k, open("k.txt"), "wb")