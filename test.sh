python index.py -i ../nltk_data/corpora/reuters/training -d dictionary.txt -p postings.txt -k 100 1> index.console.txt 2> index.log.txt
python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt 1> search.console.txt 2> search.log.txt