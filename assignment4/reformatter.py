#!/usr/bin/env python3

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado import gen, httpserver, web, netutil, process
import json
from tornado.httpclient import AsyncHTTPClient
import pickle
import xml.etree.ElementTree as ET
from optparse import OptionParser
import sys

#The reformatter is a Python module that reads in an XML Wikipedia dump and 
tree = ET.parse(sys.argv[1])
root = tree.getroot()



#outputs .in files that can be used by your MapReduce framework. The program should 
#be as simple as possible (it's a reformatter, not a preprocessor). The number of 
#files it outputs is specified by the num_partitions argument, and the path these 
#files are written to is specified by the job_path argument.
# python reformatter.py info_ret.xml \
#    --job_path=df_jobs \
#    --num_partitions=5

parser = OptionParser()
parser.add_option("--job_path", dest="jp")#, type="string")
parser.add_option("--num_partitions", dest="np")#, type="string")
(options, args) = parser.parse_args()
job_path = options.jp 
num_partitions = int(options.np)

i = -1
Partitions = []
for i in range(num_partitions):
    empty = []
    Partitions.append(empty) 

for pg in root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'):
    i+=1
    #Partitions[i%num_partitions].append(pg)
    pageDet = []
    title = pg.find('{http://www.mediawiki.org/xml/export-0.10/}title').text
    pageDet.append(title)
    ids = pg.find('{http://www.mediawiki.org/xml/export-0.10/}id').text
    pageDet.append(ids)
    for rvs in pg.findall('{http://www.mediawiki.org/xml/export-0.10/}revision'):
        txt = rvs.find('{http://www.mediawiki.org/xml/export-0.10/}text').text
        pageDet.append(txt)
    Partitions[i%num_partitions].append(pageDet)


for i in range(num_partitions):
    f = open(job_path + '/' + str(i) + '.in', 'w')
    for page in Partitions[i]:
        f.write("%s\n" % page)


#This program is clearly not scalable. It emulates the process of partitioning a 
#large input data set into small, HDFS-style blocks. Often, applications are 
#designed such that this step is not necessary at all—for example, a distributed 
#crawler could write raw data directly to distributed file system blocks, and then 
#MapReduce programs could read from these blocks directly. For other applications, 
#however, this is not feasible, and it is worthwhile to consider what this process 
#would look like for much larger data sets.







