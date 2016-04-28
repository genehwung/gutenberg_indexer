from os import path
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from cPickle import load
from machine_learning_ex.nltk_ex.gutenberg_indexer.utilities import gen_tfidf, query_cosine, merge_tfidfs, store_tf_idf
import gc
import os


def load_dump_file(path):
    print 'loading,', path
    return load(open(path, 'rb'))


def gen_tfidf_p(args):
    return gen_tfidf(*args)


def merge_and_store(tfidf, dump_paths, DUMP_PATH):
    for p in dump_paths:
        tfidf_b = load_dump_file(p)
        merge_tfidfs(tfidf, [tfidf_b])
        print 'merged size: %r'%len(tf_idf)
        gc.collect()
    store_tf_idf(tfidf, DUMP_PATH)


if __name__=='__main__':

    targetpath = r'I:\Texts\OpenAndFree\Guternberg_txt\gutenberg'
    sub_paths = list('123456789')
    targetpaths = [path.join(targetpath,s) for s in sub_paths]
    DUMP_PATH = r'J:\data_files\Gutenberg_txt_tfidf'
    book_index_path = r'I:\Texts\OpenAndFree\Guternberg_txt\gutenberg'

    loading_new = True # True
    threadPool = ThreadPool(7)
    pool = Pool(7)
    if loading_new:
        tfidfs = pool.map(gen_tfidf_p, ((p, 10000, p[-1], targetpath, True) for i, p in enumerate(targetpaths)))
        dump_paths = []
        cnt = 0
        tf_idf = {}
        for dir in os.listdir(DUMP_PATH):
            if dir.startswith('tfidf-'):
                dump_paths.append(path.join(DUMP_PATH, dir))
                cnt += 1
        merge_and_store(tf_idf, dump_paths, DUMP_PATH)
        del tf_idf
        gc.collect()