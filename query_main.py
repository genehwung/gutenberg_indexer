import os
from cPickle import load

from machine_learning_ex.nltk_ex.gutenberg_indexer.utilities import query_cosine

if __name__=='__main__':

    DUMP_PATH = r'.'
    book_index_path = r'.'

    book_index = load(open(os.path.join(book_index_path, r"book_index.all"), 'rb'))
    line2ix = load(open(os.path.join(DUMP_PATH, 'merged_ifidf_line2idx.dat'), 'rb'))
    while True:
        print '>: ',
        raw = raw_input()
        ds = query_cosine(raw, line2ix, DUMP_PATH)
        cnt = 0
        print 'query %d documents' % len(ds)
        for d in ds:
            if int(d[0]) in book_index:
                print '\t', book_index[int(d[0])], d[1], d[0]
                cnt += 1
                if cnt == 10: break