import socket
from header_structs import difuse_request, difuse_response
from json import loads, dumps


def list_dir(fd, addr, req):
    data = dumps(file_list).encode('utf-8')
    res = {}
    res['status'] = 0
    res['length'] = len(data)
    fd.sendall(difuse_response.build(res)+data)


def lookup(fd, addr, req):
    filename = req['file']
    print(filename)
    if filename == '/' or filename == None:
        res = {}
        data ={'st_mode': 16877, 'st_ctime': 1524460373.0432584, 'st_mtime': 1524460373.0432584, 'st_atime': 1524460373.0432584, 'st_nlink': 2 }
        data = dumps(data).encode('utf-8')
        res['status'] = 0
        res['length'] = len(data)
        fd.sendall(difuse_response.build(res)+data)
    elif filename not in file_list:
        res = {}
        res['status'] = 0x01
        res['length'] = 0
        print(fd)
        fd.sendall(difuse_response.build(res))
    else:
        res = {}
        data = dumps({'ip': file_ip[req['file']]}).encode('utf-8')
        res['status'] = 0
        res['length'] = len(data)
        fd.sendall(difuse_response.build(res)+data)


def join(fd, addr, req):
    for f in req:
        file_ip[f] = addr
        file_list.append(f)
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
    fd.sendall(difuse_response.build(res))


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('localhost', 8080))
        sock.listen()

        file_list = []
        file_ip = {}

        size = difuse_request.sizeof()
        print(size)

        handle = {
                0x01: list_dir,
                0x02: lookup,
                0x03: join,
                0x04: leave
            }

        while 0xDEAD:
            fd, addr = sock.accept()
            header = difuse_request.parse(fd.recv(size))
            print(header)
            payload = loads(fd.recv(header.length)) if header.length else None
            handle[header.op](fd, addr, payload)
            fd.close()
