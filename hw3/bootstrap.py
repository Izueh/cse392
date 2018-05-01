import socket
from header_structs import difuse_request, difuse_response
from json import loads, dumps
from base64 import b64encode, b64decode
from hashlib import sha1


# TODO: add salted hash
# TODO: add function to remove node if connection terminated

def list_dir(fd, addr, req):
    data = dumps(file_list).encode('utf-8')
    res = {}
    res['status'] = 0
    res['length'] = len(data)
    fd.sendall(difuse_response.build(res)+data)


def lookup(fd, addr, req):
    filename = req['file']
    file_hash = sha1(filename)
    ip = host_list[0]
    for h in host_list:
        if file_hash < h:
            ip = h
            break
    data = b64encode(dumps({'ip': ip}))
    res = {}
    res['status'] = 0
    res['length'] = 0
    res = difuse_response.build(res)
    fd.sendall(res+data)


def create(fd, addr, req):
    file_ip[req['file']] = [addr[0], 8080]
    file_list.append(req['file'])
    res = {}
    res['status'] = 0
    res['length'] = 0
    fd.sendall(difuse_response.build(res))


def remove(fd, addr, req):
    del file_ip[req['file']]
    file_list.remove(req['file'])
    res = {}
    res['status'] = 0
    res['length'] = 0
    fd.sendall(difuse_response.build(res))


def rename(fd, addr, req):
    file_ip[req['newname']] = file_ip[req['file']]
    file_list.append(req['newname'])
    del file_ip[req['file']]
    file_list.remove(req['file'])
    res = {}
    res['status'] = 0
    res['length'] = 0
    fd.sendall(difuse_response.build(res))


def join(fd, addr, req):
    ip_hash = sha1(addr[0])
    host_list.append(ip_hash)
    host_list.sort()
    hash2ip[ip_hash] = addr[0]
    # send ip of successor
    res = {}
    res['status'] = 0
    res['length'] = 0
    fd.sendall(difuse_response.build(res))


def leave(fd, addr, req):
    global file_ip
    file_ip = {k: v for k, v in file_ip.items() if v == addr}
    res = {}
    res['status'] = 0
    res['length'] = 0
    # send ip of successor to migrate
    fd.sendall(difuse_response.build(res))


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', 8081))
        sock.listen()

        file_list = []
        file_ip = {}
        host_list = []
        hash2ip = {}
        size = difuse_request.sizeof()

        handle = {
            0x01: list_dir,
            0x02: lookup,
            0x03: join,
            0x04: leave,
            0x05: create,
            0x06: remove,
            0x07: rename
        }

        while 0xDEAD:
            fd, addr = sock.accept()
            header = difuse_request.parse(fd.recv(size))
            payload = fd.recv(header.length) if header.length else None
            payload = loads(b64decode(payload))
            handle[header.op](fd, addr, payload)
            fd.close()
