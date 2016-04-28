import cPickle, os
path = r'I:\Texts\OpenAndFree\Guternberg_txt\GUTINDEX.ALL'
dir = r'I:\Texts\OpenAndFree\Guternberg_txt\gutenberg'

with open(path, 'r') as f:
    ls = f.readlines()
    book_index = {}
    for l in ls:
        try:
            l = l.strip()
            book_index[int(l[-6:].strip())] = l[:-6].strip()
        except:
            # print 'WARN: line: %r cannot be parsed'%l
            continue

    cPickle.dump(book_index, open(os.path.join(dir, r'book_index.all'),'wb'))
    print '# doc', len(book_index)

if __name__ == '__main__':
    while True:
        print '>:',
        r = raw_input()
        try:
            r = int(r)
        except:
            print 'needs to be an integer'
        if r in book_index:
            print book_index[r]
