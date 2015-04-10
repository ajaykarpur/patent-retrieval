python index.py -i ..\patsnap-corpus -d dictionary.txt -p postings.txt 1> index.console.txt 2> index.log.txt
python search.py -d dictionary.txt -p postings.txt -q q1.xml -o output.q1.txt 1> search.q1.console.txt 2> search.q1.log.txt
python search.py -d dictionary.txt -p postings.txt -q q2.xml -o output.q2.txt 1> search.q2.console.txt 2> search.q2.log.txt