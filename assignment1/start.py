import tornado.ioloop
import tornado.web
import hashlib
import getpass
import socket
from tornado import gen
from tornado.httpclient import AsyncHTTPClient


turn = 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.host)

class MainHandler2(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.host)

class MainHandler3(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.host)

class MainHandler4(tornado.web.RequestHandler):
    #Front end
    def get(self):
        self.write(self.request.host)

class GenAsyncHandler(tornado.web.RequestHandler):
    
    @gen.coroutine
    def get(self):
        name1 = "http://" + str(socket.gethostname()) + ":" + str(BASE_PORT+1) 
        name2 = "http://" + str(socket.gethostname()) + ":" + str(BASE_PORT+2) 
        name3 = "http://" + str(socket.gethostname()) + ":" + str(BASE_PORT+3) 
        global turn
        name = [name1, name2, name3]
        url = name[turn%3]
        turn += 1
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(url)
        self.write(response.body)
        

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application2 = tornado.web.Application([
        (r"/", MainHandler2),
    ])
    application3 = tornado.web.Application([
        (r"/", MainHandler3),
    ])
    application4 = tornado.web.Application([
        (r"/", GenAsyncHandler),
    ])
    MAX_PORT = 49152
    MIN_PORT = 10000
    BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
    (MAX_PORT - MIN_PORT) + MIN_PORT
    print BASE_PORT
    decor = tornado.gen.coroutine
    application.listen(BASE_PORT+1)
    application2.listen(BASE_PORT+2)
    application3.listen(BASE_PORT+3)
    application4.listen(BASE_PORT)
    
    tornado.ioloop.IOLoop.current().start()