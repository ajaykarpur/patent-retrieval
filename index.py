#!/usr/bin/python
import sys
import getopt
import os
import string
import pickle
from collections import defaultdict
import math
import nltk
import re
import itertools

stemmer = nltk.stem.porter.PorterStemmer()
# tokenizer = nltk.tokenize.WordPunctTokenizer()

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

sys.path.append("lib")
import gensim

#-------------------------------------------------------------------------------

class Indexer(object):
    def __init__(self, doc_directory, dict_filename, post_filename, k):
        self.k = k
        self.dict_filename = dict_filename
        self.post_filename = post_filename
        self.dictionary = gensim.corpora.Dictionary()
        self.corpus = []
        self.patent_mapping = {} # what if the problem is here...?

        self.stopwords = set(string.punctuation)
        with open(os.path.join("lib", "uspto_stopwords")) as s:
            self.stopwords = self.stopwords.union(set(s.read().split()))
        with open(os.path.join("lib", "custom_stopwords")) as s:
            self.stopwords = self.stopwords.union(set(s.read().split()))

        self.parse_xml(doc_directory)

        self.topic_model = gensim.models.LdaModel(self.corpus, num_topics = 500, id2word = self.dictionary)
        # self.topic_model = gensim.models.TfidfModel(self.corpus, dictionary = self.dictionary)

        self.similarity_index = gensim.similarities.Similarity("index", self.topic_model[self.corpus], num_features = self.corpus.num_terms)
        self.similarity_index.save("similarity_index")

        self.dump()

        
    def parse_xml(self, dirname):

        all_tokens = defaultdict(list)

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
                
                token_generators = []
                if "Title" in fields:
                    token_generators.append(gensim.utils.tokenize(fields["Title"], lowercase = True))
                if "Abstract" in fields:
                    token_generators.append(gensim.utils.tokenize(fields["Abstract"], lowercase = True))
                if "Assignee(s)" in fields:
                    token_generators.append(gensim.utils.tokenize(fields["Assignee(s)"], lowercase = True))
                
                for tokens in token_generators:
                    tokens = map(lambda t: stemmer.stem(t), tokens)
                    for token in tokens:
                        if token not in self.stopwords:
                            all_tokens[patent_num].append(token)

                if "IPC Class" in fields:
                    all_tokens[patent_num].append(fields["IPC Class"].strip())
                if "IPC Subclass" in fields:
                    all_tokens[patent_num].append(fields["IPC Subclass"].strip())
                if "IPC Group" in fields:
                    all_tokens[patent_num].append(fields["IPC Group"].strip())

        documents = []
        for i, (patent_num, text) in enumerate(all_tokens.iteritems()):
            documents.append(text)
            self.patent_mapping[i] = patent_num
        self.dictionary.add_documents(documents)

        # self.corpus = [self.dictionary.doc2bow(text) for document in documents]
        # corpora.MmCorpus.serialize("corpus.mm", self.corpus)

        gensim.corpora.MmCorpus.serialize("corpus.mm", [self.dictionary.doc2bow(text) for document in documents])
        self.corpus = gensim.corpora.MmCorpus("corpus.mm")

    def dump(self):
        pickle.dump(self.dictionary, open(self.dict_filename, "wb"))
        pickle.dump(self.topic_model, open(self.post_filename, "wb"))
        pickle.dump(self.patent_mapping, open("patent_mapping", "wb"))
        pickle.dump(self.stopwords, open("stopwords", "wb"))

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