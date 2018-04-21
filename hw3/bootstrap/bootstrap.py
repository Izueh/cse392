import socket
import select
from common.header_structs import difuse_request, difuse_response
from json import loads, dumps


def list_dir(fd, req):
    data = dumps(file_list).encode('utf-8')
    res = {}
    res['status'] = 0
    res['size'] = len(payload)
    fd.send_all(difuse_response.build(res)+data)


def lookup(fd, req):
    data = dumps({'ip': file_list[req['file']]})
    res = {}
    res['status'] = 0
    res['size'] = len(data)
    fd.send_all(difuse_response.build(res)+data)


def join(fd, req):
    for f in req['files']:
        file_ip[f] = req['ip']
    res = {}
    res['status'] = 0
    res['size'] = 0
    fd.send_all(difuse_response.build(res))


def leave(fd, req):
    global file_ip
    file_ip = {k: v for k, v in file_ip.items() if v == req['ip']}
    res = {}
    res['status'] = 0
    res['size'] = 0
    fd.send_all(difuse_response.build(res))


if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((socket.INADDR_ANY, 8080))
        sock.listen()

        file_list = []
        file_ip = {}

        size = difuse_request.sizeof()

        handle = {
                0x01: list_dir,
                0x02: lookup,
                0x03: join,
                0x04: leave
            }

        while 0xDEAD:
            s, _, _ = select.select([sock], [], [])
            if sock in s:
                try:
                    with sock.accept as fd:
                        header = difuse_request.parse(fd.recv(size))
                        payload = loads(fd.recv(header.size))
                        handle[header.operation](fd, payload)
                except Exception:
                    continue
