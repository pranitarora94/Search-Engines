#!/usr/bin/env python3

import sys, nltk
from nltk.tokenize import RegexpTokenizer
from collections import Counter


tokenizer = RegexpTokenizer(r'\w+')
tokenizer.tokenize('* [[Apache Wave]]')


Titles = []
Texts = []
diction = []
CollapsedTexts = []
CollapsedTitles = []
i = -1
#### TODO temporary
docIDs=[0,1,2]
num_ind  = 3

for ln in sys.stdin:
    i+=1
    lin = ln[2:-2]
    lin = lin.replace('\"', '\'')
    line = lin.split('\', \'')
    title = line[0].lower()
    Titles.append(tokenizer.tokenize(title))
    countTitle = Counter(Titles[i])
    #CollapsedTitles.append(count)
    ids = line[1]
    txt = line[2].lower()
    Texts.append(tokenizer.tokenize(txt))
    countText = Counter(Texts[i])
    #CollapsedTexts.append(count)
    #diction.append(title + ' ' + title + ' ' + title + ' ' + title + ' ' + txt)
    Count = countText + countTitle
    for term in Count:
         print('%s\t%s' % (term, ids))

