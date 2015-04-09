# patent-retrieval
A search engine for patents.

# TODO
- First, index only Title and Abstract together as one bag of words.
- Index different fields for each patent. (Come up with weighting scheme?)
- Make dictionary of term frequency and postings lists of patents.
- In postings, weight terms from different fields differently (how??).
- Alternatively, use a separate postings file for each field. Weight while searching instead of indexing.
- Give a bonus to documents that are in a similar patent class to the query.
- According to its performance in the cited paper below (Czyszczon and Zgrzywa), we chose to use the ltc.ltc scheme. In this paper, it was used in a LSI index task. (?)
- ***We are using LSI/LSA.***
- Note for Ajay: look over gensim implementation in \scripts\ and \test\ here: C:\Python27\Lib\site-packages\gensim

# resources
- http://lxml.de/performance.html
- Adam Czyszczon and Aleksander Zgrzywa, "Analysis of Web Server Retrieval Methods", New Research in Multimedia and Internet Systems, Volume 314 of Advances in Intelligent Systems and Computing, ISBN: 3319103830
- to understand LSI: http://www.puffinwarellc.com/index.php/news-and-articles/articles/33.html
- gensim LSI documentation: https://radimrehurek.com/gensim/models/lsimodel.html
- IPC guide: http://www.wipo.int/export/sites/www/classifications/ipc/en/guide/guide_ipc.pdf
- use of gensim: http://graus.nu/tag/gensim/
- use of gensim for patents: http://pyvideo.org/video/3058/exploring-patent-data-with-python