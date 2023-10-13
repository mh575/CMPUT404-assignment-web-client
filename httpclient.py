#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, Mohammed Hussain, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        print(str(self.code)+'\n'+self.body)

class HTTPClient(object):
    '''
    citations:
    url: https://docs.python.org/3/library/urllib.parse.html
    author: Python Software Foundation
    date-accessed: 11/10/23 
    license: 0BSD
    url: https://developer.mozilla.org/en-US/docs/Web/HTTP
    author: Mozilla Foundation
    date-accessed: 12/10/23
    license: CC-BY-SA 
    url: https://stackoverflow.com/questions/60739843/post-request-in-urllib-python3
    author: Erfan Taghvaei
    date-accessed: 12/10/23
    license: CC-BY-SA
    '''
    def get_host_port(self,url): 
        parsed_url = urllib.parse.urlparse(url)  

        if parsed_url.port: # check for port
            self.port = parsed_url.port
        else: # use default HTTP port
            self.port = 80

        if parsed_url.hostname: # check for host
            self.host = parsed_url.hostname 
        else: # should be caught in main
            self.host = ""
        
        if parsed_url.path: # check for path
            if parsed_url.path[-1] != "/": # path does not end in '/'
                self.path = parsed_url.path+"/" 
            else:
                self.path = parsed_url.path
        else: # no path requested
            self.path = "/"

        return None
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data.split('\r\n')[0].split(' ')[1].strip()) # get response code

        print(code) 
        return code

    def get_headers(self,data): # implemented but not required 
        headers = data.split('\r\n\r\n')[0]
        return None
    
    def get_body(self, data): 
        body = data.split('\r\n\r\n')[1] # get response body
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None): 
        code = 500
        body = ""
    
        self.get_host_port(url) 
        self.connect(self.host, self.port)

        request = "GET {} HTTP/1.1\r\nHost:{}:{}\r\nConnection: close\r\n\r\n".format(self.path, self.host, self.port)

        self.sendall(request)

        try: # decoding errors (ex. http://www.google.com/)
            response = self.recvall(self.socket)
            code = self.get_code(response)
            body = self.get_body(response)

        except Exception: 
            pass # 500 error 

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None): 
        code = 500
        body = ""

        if args == None:
            args = "" 
            args_len = 0

        else:
            args = urllib.parse.urlencode(args)
            args_len = len(args)

        self.get_host_port(url)
        self.connect(self.host, self.port)
     
        request = "POST {} HTTP/1.1\r\nHost:{}:{}\r\nContent-Length:{}\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{}\r\n\r\n".format(self.path, self.host, self.port, args_len,args)

        self.sendall(request)

        try: # decoding errors (ex. http://www.google.com/)
            response = self.recvall(self.socket)
            code = self.get_code(response)
            body = self.get_body(response)

        except Exception: 
            pass # 500 error 
        
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1): # malformed request
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3): # post
        print(client.command( sys.argv[2], sys.argv[1] ))
    else: # get
        print(client.command( sys.argv[1] ))
