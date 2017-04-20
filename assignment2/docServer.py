from assignment2 import inventory
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado import gen, httpserver, process, web, netutil
import json
from tornado.httpclient import AsyncHTTPClient
import pickle
import re



class DocHandler(tornado.web.RequestHandler):
    def initialize(self, port):
        self._port = port
    
    def get(self):
        query = str(self.get_argument('q'))
        query = query.replace("MYDELIM", " ")
        doc_id = int(self.get_argument('id'))
        #print ('query: ' + query)
        #print 'doc_id: ' + str(doc_id)
        #A document server is also an HTTP server. It receives requests via its GET method that consist of a 
        #document ID and a query. In response, it uses its document store to return detailed document data 
        #(title, URL, and snippet).
        http_client = AsyncHTTPClient()
        PartitionNum = self._port - D_BASE_PORT
        urltemp = 'http://en.wikipedia.org/wiki/'
        #print 'Partition: '
        #print PartitionNum
        Docpostings = pickle.load( open( "DocPar" + str(PartitionNum) + ".p", "rb" ) )
        if doc_id in Docpostings: #Docpostings.has_key(doc_id):
            #The snippet should be a relevant chunk of text from the document, and terms from the query should 
            #be emphasized. Don't worry too much  about cleaning up MediaWiki markup.
            result = Docpostings[doc_id][0]        ## [docIDs[i], mytitle, myURL, OrigText[i]]
            MyDict = {}
            MyDict['doc_id'] = doc_id
            MyDict['title'] = result[0]
            titleSp = result[0].split()
            isUnd = False
            myURL = urltemp
            for word in titleSp:
                if isUnd :
                    myURL = myURL + '_'
                else:
                    isUnd = True
                myURL = myURL + word

            MyDict['url'] = myURL
            MyDict['snippet'] = ''
            MyText = result[0] + result[1]
            Qu = query.split(' ')
            snippetStart = -1
            found_one_term = False
            for term in Qu:
                #print ('term is: ' + term)

                positions = [m.start() for m in re.finditer(term.lower(), MyText.lower())]
                #print ('poses: ')
                #print (positions)
                if (len(positions) >0):
                    found_one_term = True
                    for i in range(len(positions)):
                        #print positions[i]
                        newPos = [m.start() for m in re.finditer(term.lower(), MyText.lower())]
                        pos = newPos[i]
                        begin = pos-1 if pos else 0
                        MyText = MyText[:begin] + ' <strong>' + MyText[pos:pos +len(term)] + '</strong> ' + MyText[pos +len(term)+1:]
                        if snippetStart < 0:
                            snippetStart = begin-50 if begin>50 else 0
                        else: 
                            if pos<snippetStart:
                                snippetStart += 19

                    snippet = ''
                    #print MyText
                    if snippetStart >0:
                        while (MyText[snippetStart] != ' '):
                            snippetStart +=1
                        snippet = '... '
                    if(len(MyText) > snippetStart+400):
                        snipend = snippetStart + 400
                        while (MyText[snipend] != ' '):
                            snipend +=1
                        snippet += MyText[snippetStart:snipend]
                        if(len(MyText) > snippetStart+400):
                            snippet += ' ...'
                    else: 
                        snippet += MyText[snippetStart:]
                    MyDict['snippet'] += snippet
            if found_one_term == False:
                    self.write('exception: term not found in document')
                    print ('could not find term ' + str(doc_id) + ' ' + str(term))
                    self.write(MyText)
                    print (MyText)
                    print (len(result))
            RS = [MyDict]
            self.write(json.JSONEncoder().encode({"results": RS}))            ### print as a dictionary
        else:
            ### Raise exception
            self.write('exception: document not found')            ### print as a dictionary
            print ('could not find ' + str(doc_id))
            ###  ##
            ##print 'well, \033[1m' + 'Hello \033[0m there' 
            ####
            

#The output should be JSON-encoded
    

if __name__ == "__main__":

    task_id = process.fork_processes(inventory.num_doc)
    
    D_BASE_PORT = inventory.port2 
    port = D_BASE_PORT + task_id 

    app = httpserver.HTTPServer(web.Application([web.url(r"/doc", DocHandler, dict(port=port))]))
    app.add_sockets(netutil.bind_sockets(port))
    print ('docServer' + str(task_id) + ' at port: ' + str(port))
    tornado.ioloop.IOLoop.current().start()