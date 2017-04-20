import tornado.ioloop
import tornado.web
import tornado.httpserver
import hashlib
import getpass
import socket
from tornado import gen, httpserver, process
import json
from assignment2 import inventory
import os
from tornado.httpclient import AsyncHTTPClient

#class MainHandler(tornado.web.RequestHandler):
#    def get(self):
#        self.write(self.request.host)
SETTINGS = {'static_path': "webapp/"}

class FrontEndHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        name = self.get_argument('q', None)
        print ('searching for ' + str(name))
        name = name.replace(" ", "MYDELIM")
        #print socket.gethostname()
        #port1 = 35315
        #url = "http://linserv2.cims.nyu.edu:" + str(port1) + "/index?q=" + str(name)
        http_client = AsyncHTTPClient()
        postings = []
        for temp_url in inventory.indUrl:
            url = "http://%s:%s%s" % (socket.gethostname(),temp_url, name)#"http://linserv2.cims.nyu.edu:" + str(port1 + i) + "/index?q=" + str(name)
            #print ('query ')
            #print (url)
            response = yield http_client.fetch(url)
            resp = json.loads(response.body.decode())
            #resp = json.JSONDecoder().decode(response.body)
            postList = resp['postings']
            #print ('got postings')
            #print 'PostLength from ' + temp_url
            #print len(postList)
            listText = response.body[15:-3]
            for post in postList:
                int1 = int(post[0])
                int2 = float(post[1])
                intpair = [int2,int1]
                postings.append(intpair)
        postings.sort(reverse=True)
        topPostings = []
        if len(postings) >= 10:
            topPostings = postings[:10]
        else:
            topPostings = postings
#        print topPostings

        results = []
        for posting in topPostings:
            DocID = posting[1]
            docPartNum = DocID% inventory.num_doc
            temp_url = inventory.docUrl[docPartNum] 
            #temp_url = "http://linserv2.cims.nyu.edu:" + str(DocServer) + "/doc?id=" 

            url = "http://" + str(socket.gethostname()) + ":" + temp_url + str(DocID) + "&q=" + str(name)
            print (url)
            response = yield http_client.fetch(url)
            listText = response.body[14:-3]
            resp = json.loads(response.body.decode())
            #resp = json.JSONDecoder().decode(response.body)
            DocList = resp['results'][0]
            a = []
            a.append(DocList['snippet'])
            a.append(DocList['title'])
            a.append(DocList['doc_id'])
            a.append(DocList['url'])
            results.append(DocList)

        self.finish(json.JSONEncoder().encode({"num_results": len(results), "results": results}))
        #print 'Results: '
        print (str(len(results)) + ' results found!' )

if __name__ == "__main__":

    task_id = process.fork_processes(3)
    if(task_id ==0):
    
        application = tornado.web.Application([
            (r"/search", FrontEndHandler)
        ], **SETTINGS)
        MAX_PORT = 49152
        MIN_PORT = 10000
        BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
        (MAX_PORT - MIN_PORT) + MIN_PORT
        print ('FrontEnd at port: ' + str(BASE_PORT))
        print ('Host name: ' + str(socket.gethostname()))
        application.listen(BASE_PORT)
    elif task_id == 1:
        os.system('python3.6 -m assignment2.indexServer')
    else:
        os.system('python3.6 -m assignment2.docServer')

    tornado.ioloop.IOLoop.current().start()