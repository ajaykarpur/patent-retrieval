# patent-retrieval
A search engine for patents.

# TODO
- Index different fields for each patent. (Come up with weighting scheme?)
- Make dictionary of term frequency and postings lists of patents.
- In postings, weight terms from different fields differently (how??).
- Alternatively, use a separate postings file for each field. Weight while searching instead of indexing.
- Give a bonus to documents that are in a similar patent class to the query.
- Use idf for query.

# resources
- http://lxml.de/performance.html