import socket
from json import dumps, loads
from header_structs import difuse_request, difuse_response
import os
from sys import argv
from threading import Thread
from hashlib import sha1
from base64 import b64encode, b64decode
import logging
import sys


# TODO: add file migration functionality
def reqboot(op, data):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.connect((argv[1], int(argv[2])))

    data = dumps(data).encode('utf-8')
    res = {}
    res['op'] = op
    res['length'] = len(data)
    request = difuse_request.build(res)
    serversocket.sendall(request + data)


def join():
    s = socket.socket()
    s.connect((argv[1], int(argv[2])))
    h = difuse_request.build({'op': 0x3, 'length': 0})
    s.sendall(h)
    h = s.recv(difuse_response.sizeof())
    h = difuse_response.parse(h)
    data = s.recv(h.length)
    logging.debug(f'data: {data}')
    data = loads(data.decode('utf-8'))
    if data:
        recv_files(data['ip'], data['id'])

    # TODO: receive and call recv_files


def leave():
    s = socket.socket()
    s.connect((argv[1], int(argv[2])))
    h = difuse_request.build({'op': 0x4, 'length': 0})
    s.sendall(h)
    h = s.recv(difuse_response.sizeof())
    h = difuse_response.parse(h)
    data = s.recv(h.length)
    data = loads(data.decode('utf-8'))
    if data:
        s.connect((data['ip'], 8080))
        data = dumps({'hash': myhash}).encode('utf-8')
        h = difuse_request.build({'op': 0x17, 'length': 0})
        s.sendall(h + data)


def read(fd, req, addr):
    with open('/'.join((file_dir, req['file'])), 'rb') as f:
        f.seek(req['offset'])
        data = f.read(req['size'])
        res = {}
        res['status'] = 0
        res['length'] = len(data)
        fd.sendall(difuse_response.build(res) + data)


def write(fd, req, addr):
    with open('/'.join((file_dir, req['file'])), 'w+') as f:
        f.seek(req['offset'])
        f.write(req['data'])
        res = {}
        res['status'] = 0
        res['length'] = 0
        fd.sendall(difuse_response.build(res))


def list_files(fd, req, addr):
    data = dumps(os.listdir(file_dir)).encode('utf-8')
    res = {}
    res['status'] = 0
    res['length'] = len(data)
    res = difuse_response.build(res)
    fd.sendall(res + data)


def truncate(fd, req, addr):
    with open('/'.join((file_dir, req['file'])), 'w+') as f:
        f.truncate(req['size'])
        res = {}
        res['status'] = 0
        res['length'] = 0
        fd.sendall(difuse_response.build(res))


def rename(fd, req, addr):
    os.rename('/'.join((file_dir, req['file'])),
              '/'.join((file_dir, req['newname'])))

    res = {}
    res['status'] = 0
    res['length'] = 0
    h = difuse_response.build(res)
    fd.sendall(h)


def stat(fd, req, addr):
    filepath = '/'.join((file_dir, req['file']))
    data = {}
    if(os.path.isfile(filepath)):
            info = os.stat(filepath)
            stat = dict(st_mode=info.st_mode, st_nlink=info.st_nlink,
                        st_size=info.st_size, st_ctime=info.st_ctime,
                        st_mtime=info.st_mtime, st_atime=info.st_atime)
            data = stat
    data = dumps(data).encode('utf-8')
    res = {}
    res['status'] = 0
    res['length'] = len(data)
    h = difuse_response.build(res)
    fd.sendall(h + data)

def rm(fd, req, addr):
    data = {'file': req['file']}
    os.unlink('/'.join((file_dir, req['file'])))

    res = {}
    res['status'] = 0
    res['length'] = 0
    h = difuse_response.build(res)
    fd.sendall(h)


def recv_help(ip, my_hash):
    logging.debug(f'ip: {ip}')
    logging.debug(f'hash: {my_hash}')
    s = socket.create_connection((ip, 8080))
    listenfd = socket.socket()
    listenfd.bind(('0.0.0.0', 0))
    listenfd.listen()
    port = listenfd.getsockname()
    logging.debug(f'port: {port[1]}')
    data = dumps({'port': port[1], 'hash': my_hash}).encode('utf-8')
    req = {}
    req['op'] = 0x16
    req['length'] = len(data)
    req = difuse_request.build(req)
    s.sendall(req+data)
    s.close()
    s, conn = listenfd.accept()
    while(1):
        h = s.recv(difuse_request.sizeof())
        if not h:
            break
        h = difuse_request.parse(h)
        data = s.recv(h.length)
        data = loads(data)
        data['data'] = b64decode(data['data'])
        f = open(data['fname'], 'wb')
        f.write(data['data'])
        f.close()
    s.close()
    listenfd.close()


def recv_files(ip, ip_hash):
    t = Thread(target=recv_help, args=[ip, ip_hash])
    t.start()


def get_files(fd, req, addr):
    t = Thread(target=recv_help, args=[addr[1], req['hash']])
    t.start()


def send_help(ip, port, other_hash):
    files = os.listdir(file_dir)
    logging.debug(f'port: {port}')
    with socket.create_connection((ip, port)) as s:
        for fname in files:
            h = sha1(fname.encode('utf-8')).digest()
            h = int.from_bytes(h, byteorder='little')
            print(h)
            if h < other_hash:
                fname = '/'.join((file_dir, fname))
                f = open(fname, 'rb')
                data = b64encode(f.read().decode('utf-8'))
                f.close()
                os.unlink(fname)
                data = dumps({'fname': fname, 'data': data})
                req = {'op': 0, 'length': len(data)}
                req = difuse_request.build(req)
                s.sendall(req+data)


def send_files(fd, req, addr):
    t = Thread(target=send_help, args=[addr[0], req['port'], req['hash']])
    t.start()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', 8080))
        sock.listen()
        myhash = 0
        size = difuse_request.sizeof()

        handle = {
            0x10: stat,
            0x11: read,
            0x12: write,
            0x13: truncate,
            0x14: rm,
            0x15: rename,
            0x16: send_files,
            0x17: get_files,
            0x18: list_files
        }

        file_dir = 'difuse.local'

        join()

        while 0xCAFE:
            fd, addr = sock.accept()
            payload = None
            header = difuse_request.parse(fd.recv(size))
            if header.length:
                payload = fd.recv(header.length)
                payload = loads((payload).decode('utf-8'))
            handle[header.op](fd, payload, addr)
            fd.close()
