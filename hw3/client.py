from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import socket
import os
from json import loads, dumps
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from header_structs import difuse_request, difuse_response

class Memory(LoggingMixIn, Operations):

    """Example memory filesystem. Supports only one level of files."""
    def __init__(self):
        print("init")
        self.files = {}
        self.data = defaultdict(str)
        self.fd = 0
        now = time()
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                st_mtime=now, st_atime=now, st_nlink=2)

    """HELPER FUNCTION"""
    def requestboot(self, op, data):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.connect((ip, port))
        data = dumps(data)
        res = {}
        res['op'] = op
        res['length'] = len(data)
        request = difuse_request.build(res)
        req_data = request + data.encode('utf-8')
        serversocket.sendall(req_data)

        res = serversocket.recv(difuse_response.sizeof())
        res_header = difuse_response.parse(res)
        if res_header.status == 1:
            raise FuseOSError(ENOENT)
        st = {}
        if(res_header.length):
            st = serversocket.recv(res_header.length)
            st = st.decode('utf-8')
            st = loads(st)
        return st

    def chmod(self, path, mode):
        print("chmod")
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        print("chown")
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        print("create")
        attr = dict(st_mode=(S_IFREG | mode), st_nlink=1,
             st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time())
        data = {'file': path[1:],
                'attributes': attr}
        self.requestboot(0x5, data)
        return os.open(saving_path + path, os.O_WRONLY | os.O_CREAT, mode)

    def getattr(self, path, fh=None):
        print('getattr', path)
        if path != '/':
            path = path[1:]
        data = {'file': path}
        attr = self.requestboot(0x2, data)
        #if path not in self.files:
        #    raise FuseOSError(ENOENT)
        #st = self.files[path]
        return attr['attr']

    def getxattr(self, path, name, position=0):
        print("getxattr")
        attrs = self.files[path].get('attrs', {})
        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        print("listxattr")
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        print("mkdir")
        self.files[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time())
        self.files['/']['st_nlink'] += 1

    def open(self, path, flags):
        print("open")
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        print("read")
        data = {'file': path}
        attr = self.requestboot(0x2, data)
        ip = attr['ip']
        return self.data[path][offset:offset + size]

    def readdir(self, path, fh):
        print('readdir')
        st = self.requestboot(0x1, {})
        return ['.', '..'] + st

    def readlink(self, path):
        print("readlink")
        return self.data[path]

    def removexattr(self, path, name):
        print("removexattr")
        attrs = self.files[path].get('attrs', {})
        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        print("rename")
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        print("rmdir")
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        print("setxattr")
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        print("statfs")
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        print("syslink")
        self.files[target] = dict(st_mode=(S_IFLNK | 0o777), st_nlink=1,
            st_size=len(source))
        self.data[target] = source

    def truncate(self, path, length, fh=None):
        print("truncate")
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length

    def unlink(self, path):
        print("unlink")
        self.files.pop(path)

    def utimens(self, path, times=None):
        print("utimens")
        now = time()
        atime, mtime = times if times else (now, now)
        data = {'atime': atime, 'mtime': mtime}
        print(data)
        #self.requestboot(0x07, data)


    def write(self, path, data, offset, fh):
        print("write")
        self.data[path] = self.data[path][:offset] + data
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)


if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 8081
    saving_path = '/home/jappatel/mount/save'
    fuse = FUSE(Memory(), argv[1], foreground=True)
