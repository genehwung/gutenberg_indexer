import os, sys, gc, time
import cPickle as pickle
from collections import defaultdict, Counter
from operator import itemgetter
import logging
from nltk import word_tokenize, PorterStemmer, LancasterStemmer, tokenize

logging.basicConfig(format='%(funcName)s,%(lineno)d:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def read_file(path):
    '''
    read the file at the path, convert it to unicode, skip the boilerplate
    :param path: string: the absolute path to the txt file
    :return: list[string]: each is a paragraph
    Example: paragraphs = read_file(r'D:\test.txt')
    '''
    try:
        paragraphs = []
        start_flg = False
        codec = None
        with open(path, 'r') as f:
            paragraph = []
            lines = f.readlines()
            for line in lines:
                if line.find('Character set encoding:') >= 0:
                    codec = line[len('Character set encoding:'):].strip().lower()
                if codec == 'ascii' or not codec or codec.startswith('utf-8'):
                    line.decode('utf-8')
                else:
                    line = line.decode(codec)
                if line.find('START OF ') >= 0 and line.find(u'PROJECT GUTENBERG EBOOK')>=0 and line.find('***')>=0:
                    start_flg = True
                    continue
                elif line.find('END OF ') >= 0 and line.find(u'PROJECT GUTENBERG EBOOK')>=0 and line.find('***')>=0:
                    break
                if start_flg and line[:-1]:
                    paragraph.append(line[:-1].strip())
                if paragraph and line == u'\n':
                    paragraphs.append(u' '.join(paragraph))
                    paragraph = []
        return paragraphs
    except: return []


def tokenize_normalize(raw):
    '''
    tokenize raw texts
    :param raw: unicode string
    :return: list[unicode]: a list of tokenized unicode
    Example: words = tokenize_normalize(line)
    '''
    tokens = [t for t in word_tokenize(raw) if len(t) < 20]  # don't use any token too long (like genetic sequence)
    porter = PorterStemmer()
    tokens_n = [porter.stem(t) for t in tokens if t[0].isalpha()]  # only interested in word
    tokens_n = ['NUMBER' if all(a.isdigit() for a in t) else t for t in tokens_n]  # combine all numbers to one
    return tokens_n


def normalize(word):
    '''
    normalize the the word for query or indexing
    :param word: unicode string
    :return: unicode string of the normalized ter
    '''
    porter = PorterStemmer()
    return porter.stem(word) if word[0].isalpha() else ''


def get_inverted_index(paragraphs):
    '''
    example code to generate inverted index, not used, using tf-idf instead.
    :param paragraphs: take multiple paragraphs (each paragraph is taken as a document)
    :return: a dict[term] -> (freq, paragraph id)
    '''
    inverted_index = defaultdict(lambda: (0, []))
    for i, p in enumerate(paragraphs):
        tokens_n = tokenize_normalize(p)
        for t in tokens_n:
            tmp = inverted_index[t]
            if not tmp[1] or tmp[1][-1] != i:
                tmp[1].append(i)
                inverted_index[t] = (tmp[0]+1, tmp[1])
    return inverted_index


def sqrt_(x):
    '''
    sqrt without any floating point arithmatic to avoid long integer computation
    :param x:
    :return:
    '''
    lower, upper = 0, x+1
    # upper = lower + 1 can cause infinite loop, this is the result of this kind of binary search
    while lower < upper:
        mid = (lower+upper)/2
        temp = mid*mid
        if temp == x:
            return mid
        elif temp > x:
            upper = mid
        else:
            lower = mid+1

    return lower if lower**2 < x else lower-1


def update_tf_idf(paragraphs, tf_idf, d_len, doc_id):
    ''' return document geometry mean '''
    freq = Counter()
    for i, p in enumerate(paragraphs):
        tokens_n = tokenize_normalize(p)
        freq.update(tokens_n)
    doc_len = sqrt_(sum(f ** 2 for f in freq.values()))
    if 'the' not in freq: logger.warn('WARN: doc %r, has not "the", with paragraphs %r'%(doc_id,len(paragraphs)))
    for t in freq:
        if t not in tf_idf:
            tf_idf[t] = (0, {})
        doc_list = tf_idf[t][1]
        doc_list[doc_id] = freq[t]*1./doc_len
        tf_idf[t] = (tf_idf[t][0]+freq[t], doc_list)
    d_len[doc_id] = doc_len


def gen_tfidf(targetpath, num_doc=1000, file_id=0, dumppath=0, save=False):
    cnt =  0
    tfidf = {} # defaultdict(lambda: (0, defaultdict(int)))  # a frequency and document frequency
    doc_len = {}
    for path, dirnames, filenames in os.walk(targetpath):
        for filename in filenames:
            try:
                if filename.endswith('.txt') and filename.find('-') == -1 and any(a.isdigit() for a in filename[:-4]):
                    paragraphs = read_file(os.path.join(path, filename))
                    if not paragraphs: continue
                    doc_id = int(filename[:-4].strip())
                    update_tf_idf(paragraphs, tfidf, doc_len, doc_id)
                    cnt += 1
                    logger.info('worker for file %s is at %d file'%(file_id, cnt))
                    if cnt % 200 == 0 and file_id and save:
                        pickle.dump(tfidf, open(os.path.join(dumppath, 'tfidf-%s-%d.dat' % (file_id, cnt)), 'wb'))
                        tfidf = {}
                        gc.collect()
            except:
                logger.warn('warn: filename %r went wrong, gave up and continue'%filename)
                continue
            if cnt >= num_doc: break
        if cnt >= num_doc: break
    if cnt %200:
        try: pickle.dump(tfidf, open(os.path.join(dumppath, 'tfidf-%s-%d.dat' % (file_id, cnt)), 'wb'))
        except: logger.warn('WARN: last dump was not working, no big deal')
    return tfidf


def merge_tfidfs(tf_idf, tf_idfs):
    if tf_idfs:
        for i in xrange(len(tf_idfs)):
            for t, fq_df_i in tf_idfs[i].items():
                if t not in tf_idf:
                    tf_idf[t] = (0, {})
                fq_df = tf_idf[t]
                fq_df[1].update(fq_df_i[1])
                tf_idf[t] = (fq_df_i[0] + fq_df[0], fq_df[1])


def read_tf_idf(path):
    ''' type: string -> dict '''
    logger.info('reading at %r'%path)
    with open(path, 'r') as f:
        lines = f.readlines()
    if not lines: return {}
    tfidf = {}
    for i, l in enumerate(lines):
        words = l.split()
        term = words[0]
        freq_total = int(words[1])
        doc_df = {}
        for i in xrange(2, len(words)):
            docid, df = words[i].split(':')
            doc_df[int(docid)] = float(df)
        tfidf[term] = (freq_total, doc_df)
    return tfidf


def store_tf_idf(tfidf, path):
    logger.info('writing merged tfidf to %r'%path)
    if not os.path.isdir(path): os.makedirs(path)
    with open(os.path.join(path, 'merged_ifidf.txt'), 'w') as f:
        f.write('')
    tfdif_pair = sorted(tfidf.items())
    lines, line2ix = [], {}
    cnt = 0
    for t, fqdf in tfdif_pair:
        line = [t, str(fqdf[0])]
        for doc, val in sorted(fqdf[1].items()):
            line.append(str(doc) + ':' + str(val))
        line2ix[t] = cnt
        line = (' '.join(line) + '\n').encode('utf-8')
        lines.append(line)
        cnt += len(line)+1
        if len(lines) == 100000:
            with open(os.path.join(path, 'merged_ifidf.txt'), 'a') as f:
                for l in lines: f.write(l)
                lines = []
    with open(os.path.join(path, 'merged_ifidf.txt'), 'a') as f:
        for l in lines: f.write(l)
    pickle.dump(line2ix, open(os.path.join(path, 'merged_ifidf_line2idx.dat'), 'wb'))


def query_cosine(query, line2ix, path, top=10):
    f = open(os.path.join(path, 'merged_ifidf.txt'), 'r')
    ts = tokenize_normalize(query)
    freq = Counter(ts)
    rst = {}
    for t in freq:
        if t not in line2ix: return []
        f.seek(line2ix[t])
        line = f.readline().decode('utf-8')
        ps = [pattern for pattern in line.split() if pattern.find(':')!=-1]
        for p in ps:
            docid, tf= p.split(':')
            docid, tf = int(docid), float(tf)
            if docid not in rst: rst[docid] = 0
            rst[docid] += 1.* tf * freq[t] / (len(ps)-2)
    return sorted(rst.items(), key=itemgetter(1), reverse=True)


# def query_cosine(query, tfidf, top=10):
#     ts = tokenize_normalize(query)
#     freq = Counter(ts)
#     rst = {}  #defaultdict(int)
#     for t in freq:
#         if t in tfidf:
#             for docid, tf in tfidf[t][1].items():
#                 if docid not in rst: rst[docid] = 0
#                 rst[docid] += 1.* tf * freq[t] / len(tfidf[t][1])
#     return sorted(rst.items(), key=itemgetter(1), reverse=True)


def query_inverted_index(inverted_index, words):
    # TODO: use merge sort algorithm for less memory requirement
    if not words: return []
    words = [normalize(w) for w in words]
    rst = {a for a in inverted_index[words[0]][1]}
    for i in xrange(1, len(words)):
        rst &= {a for a in inverted_index[words[i]][1]}
    return rst


if __name__ == '__main__':
    targetpath = r'I:\Texts\OpenAndFree\Guternberg_txt\gutenberg'
    # tfidf = gen_tfidf(targetpath)
    # pickle.dump(tfidf, open(os.path.join(targetpath,r'ifidf.data'), 'wb'))
    book_index = pickle.load(open(os.path.join(targetpath, r"book_index.all"), 'rb'))
    tfidf = pickle.load(open(os.path.join(targetpath, r'ifidf.data'), 'rb'))
    while True:
        print '>: ',
        raw = raw_input()
        cnt = 0
        try:
            ds = query_cosine(raw, tfidf)
            print 'query %d documents' % len(ds)
            for d in ds:
                # print d
                if int(d[0].strip()) in book_index:
                    print '\t', book_index[int(d[0].strip())], d[1], d[0]
                    cnt += 1
                    if cnt == 10: break
        except:
            print 'something went wrong'
            continue


