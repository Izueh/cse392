import socket
import select
from json import dumps, loads
from common.header_structs import difuse_request, difuse_response


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((socket.ADDR_ANY, 8080))
        sock.listen()

        size = difuse_request.sizeof()

        handle = {}

        file_dir = 'difuse.local'

        while 0xCAFE:
            s, _, _ = select.select([sock], [], [])
            if sock in s:
                try:
                    with sock.accept() as fd:
                        header = difuse_request.parse(fd.recv(size))
                        payload = loads(fd.recv(header.size))
                        handle[header.op](fd, payload)
                except Exception:
                    continue
