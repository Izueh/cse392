import socket
import select
from json import dumps, loads
from header_structs import difuse_request, difuse_response
import os
from sys import argv

def join():
    s = socket.socket()
    s.connect((argv[1], int(argv[2])))
    data = dumps(os.listdir(file_dir)).encode('utf-8')
    h = difuse_request.build({'op': 0x3, 'length': len(data)})
    s.sendall(h+data)

def read(fd, req):
    with open('/'.join((file_dir, req['file'])), 'rb') as f:
        f.seek(req['offset'])
        data = f.read(req['size'])
        res = {}
        res['status'] = 0
        res['length'] = len(data)
        fd.sendall(difuse_response.build(res) + data)


def write(fd, req):
    with open('/'.join((file_dir, req['file'])), 'w+') as f:
        f.seek(req['offset'])
        f.write(req['data'])
        res = {}
        res['status'] = 0
        res['length'] = 0
        fd.sendall(difuse_response.build(res))

def truncate(fd, req):
    with open('/'.join((file_dir, req['file'])), 'w+') as f:
        f.truncate(req['size'])
        res = {}
        res['status'] = 0
        res['length'] = 0
        fd.sendall(difuse_response.build(res))


def stat(fd, req):
    info = os.stat('/'.join((file_dir, req['file'])))
    stat = dict(st_mode=info.st_mode, st_nlink=info.st_nlink,
                           st_size=info.st_size, st_ctime=info.st_ctime,
                           st_mtime=info.st_mtime, st_atime=info.st_atime)
    data = dumps(stat).encode('utf-8')
    res = {}
    res['status'] = 0
    res['length'] = len(data)
    h = difuse_response.build(res)
    fd.sendall(h + data)


def rm(fd, req):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.connect((argv[1], int(argv[2])))

    data = dumps({'file': req['file']}).encode('utf-8')
    res = {}
    res['op'] = 0x06
    res['length'] = len(data)
    request = difuse_request.build(res)
    serversocket.sendall(request + data)

    os.unlink('/'.join((file_dir, req['file'])))

    res = {}
    res['status'] = 0
    res['length'] = 0
    h = difuse_response.build(res)
    fd.sendall(h)

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 8080))
        sock.listen()

        size = difuse_request.sizeof()

        handle = {
            0x10: stat,
            0x11: read,
            0x12: write,
            0x13: truncate,
            0x14: rm
        }

        file_dir = '/home/jappatel/mount/save'

        join()

        while 0xCAFE:
            fd, addr = sock.accept()
            header = difuse_request.parse(fd.recv(size))
            payload = loads(fd.recv(header.length))
            handle[header.op](fd, payload)
