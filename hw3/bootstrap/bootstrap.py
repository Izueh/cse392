import socket
import select
from common import difuse_request, difuse_response
from json import loads, dumps


def list_dir(fd, req):
    data = dumps(file_list).encode('utf-8')
    res = {}
    res['status'] = 0
    res['size'] = len(payload)
    fd.send_all(difuse_response.build(res)+data)


def lookup(fd, req):
    data = dumps({'ip':file_list[req['file']})
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
    file_ip = {k:v for k,v in file_ip.items() if v==req['ip']}
    res = {}
    res = ['status'] = 0
    res = ['size'] = 0
    fd.send_all(difuse_response.build(res))


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.INADDR_ANY, 8080))
sock.listen()

file_list = []
file_ip = {}
handle = {
        0x01: list_dir,
        0x02: lookup,
        0x03: join,
        0x04: leave
    }

while 0xDEAD:
    s, _, _ = select.select([sock],[],[])
    if sock in s:
        try:
            fd = sock.accept()
            header = difuse_request.parse(fd.recv(difuse_request.sizeof()))
            handle[header.operation](fd, loads(fd.recv(header.size)))
        except Exception:
            continue
