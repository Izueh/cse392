import socket
import select
from json import dumps, loads
from common.header_structs import difuse_request, difuse_response


def read(fd, req):
    with open('/'.join((file_dir, req['file'])), 'rb') as f:
        f.seek(req['offset'])
        data = f.read(req['size'])
        res = {}
        res['status'] = 0
        res['length'] = len(data)
        fd.send_all(difuse_response.build(res) + data)


def write(fd, req):
    with open('/'.join((file_dir, req['file'])), 'rb') as f:
        f.seek(req['offset'])
        f.write(req['data'])
        res = {}
        res['status'] = 0
        res['length'] = 0
        fd.send_all(difuse_response.build(res))


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((socket.ADDR_ANY, 8080))
        sock.listen()

        size = difuse_request.sizeof()

        handle = {}

        file_dir = 'difuse.local'

        while 0xCAFE:
            fd, addr = sock.accept()
            header = difuse_request.parse(fd.recv(size))
            payload = loads(fd.recv(header.size))
            handle[header.op](fd, payload)
