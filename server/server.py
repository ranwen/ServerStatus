import select
import socket
import requests
import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import re
import threading
import signal
import sys
import random

def writefile(fi,content):
    f=open(fi,'w')
    f.write(content)
    f.close()

def readfile(fi):
    f=open(fi)
    gg=f.read()
    f.close()
    return gg

def auth(usap):
    try:
        name,pwd=usap.split(b':')
        name=name.decode()
        pwd=pwd.decode()
        rin=-1
        for i in range(0,len(config['node'])):
            if config["node"][i]["name"]==name:
                rin=i
                break
        print(name,pwd,rin)
        if rin==-1:
            return -1
        if config["node"][rin]["pwd"]==pwd:
            return rin
        return -1
    except:
        print("ERR :"+usap.decode())
        return -1

stat=[]
lock = threading.Lock()

class TCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global stat
        s=self.request
        x=s.recv(1024)
        print(x)
        if x==b'Client':
            s.sendall(b"Authentication required")
            nid=auth(s.recv(1024))
            if nid==-1:
                s.sendall(b"Failed")
                return
            s.sendall(b"Authentication successful")
        stat[nid].update({"status":True})
        while True:
            data = s.recv(4096)
            if len(data)<=0:
                lock.acquire()
                stat[nid].update({"status":False})
                lock.release()
                break
            lock.acquire()
            stat[nid].update(json.loads(data))
            lock.release()
            print(data)





def htc(m):
    return chr(int(m.group(1),16))
 
def urldecode(url):
    rex=re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M)
    return rex.sub(htc,url)
 
def parsehttpparam(fuck):
    shit=fuck.split('&')
    ret=dict()
    for sbkh in shit:
        ss=sbkh.split('=')
        ret[ss[0]]=ss[1]
    return ret

class SETHandler(BaseHTTPRequestHandler):
    def rf(self,fi):
        f=open(fi,"rb")
        gg=f.read()
        f.close()
        return gg
    def _set_response(self):
        self.send_response(200)
        if not str(self.path).find("."):
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return

        ext=os.path.splitext(self.path)[1]
        if ext=='.js':
            self.send_header('Content-type', 'application/x-javascript')
        elif ext=='.css':
            self.send_header('Content-type', 'text/css')
        elif ext=='.woff':
            self.send_header('Content-type', 'application/octet-stream')
        else:
            self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print("GET request,\nPath: %s\nHeaders:\n%s\n"%(str(self.path), str(self.headers)))
        global stat,config
        if self.path=='/':
            self._set_response()
            self.wfile.write(self.rf("web/index.html"))
            return
        if self.path=='/stats.json':
            res={"servers":stat,"updated":int(time.time())}
            self._set_response()
            self.wfile.write(json.dumps(res).encode())
            return
        if self.path.find("../")!=-1:
            self.send_response(404)
            self.end_headers()
            return
        if len(self.path)>6 and self.path[0:4]=='/add':
            try:
                ff=self.path.split('?')[1]
                lis=parsehttpparam(ff)
                if lis["token"]!=config["token"]:
                    self.send_response(404)
                    self.end_headers()
                user=lis["name"]
                pwd=random.random()
                lock.acquire()
                stat.append({"name":user,"status":False})
                config["node"].append({"name":user,"pwd":pwd})
                writefile("config.json",json.dumps(config,indent=2))
                lock.release()
                self._set_response()
                cao=self.rf("web/install.sh")
                cao.replace(b"VNAME",user.encode())
                cao.replace(b"VPASS",str(random).encode())
                cao.replace(b"VSERVERIP",self.headers["Host"].encode())
                self.wfile.write(cao)
            except:
                self.send_response(404)
                self.end_headers()
                return
        if os.path.isfile("./web"+self.path):
            self._set_response()
            self.wfile.write(self.rf("./web"+self.path))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

config=json.loads(readfile("config.json"))
HTTP_PORT=config["http_port"]
SERVER_PORT=config["server_port"]
for i in config["node"]:
    stat.append({"name":i["name"],"status":False})

socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(('', SERVER_PORT), TCPHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

httpd = HTTPServer(('', HTTP_PORT), SETHandler)

httpd_thread = threading.Thread(target=httpd.serve_forever)
httpd_thread.daemon = True
httpd_thread.start()

def handler(signum, _):
    print("QUIT")
    server.server_close()
    httpd.server_close()
    sys.exit(0)
signal.signal(signal.SIGINT,handler)

while 1:
    time.sleep(1)