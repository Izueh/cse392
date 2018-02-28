import socket

def read(fd):
    msg = b''
    while not msg.endswith(b'\r\n\r\n'):
        msg += fd.recv(1)
    return msg


def listen(address):
    s = None
    for res in socket.getaddrinfo(address[0], address[1], socket.AF_UNSPEC, \
            socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(1)
        except OSError as msg:
            s.close()
            s = None
            continue
        break
    return s

def login():
    fd = login_queue.get()
    try:
        buf = fd.recv(8)
        cmd = buf.split('\r\n\r\n')[0]
        if cmd != b'ME2u':
            raise Exception()
        fd.sendall(b'U2EM\r\n\r\n')
        buf = fd.recv(18)
        cmd,msg = buf.split(b' ')
        if cmd != b'IAM':
            raise Exception()
        name = msg.split(b'\r\n\r\n')[0]
        if name in users:
            fd.sendall(b'ETAKEN\r\n\r\n')
            fd.close()
            return
        fds[name] = fd
        users[fd] = name
        fd.sendall(b'MAI\r\n\r\n')
        fd.sendall(f'MOTD {MOTD}\r\n\r\n'.encode())
        epoll.register(fd)
    except:
        fd.close()

def send_ot():
    print('send_ot')
    return

def send_utsil():
    print('send_utsil')
    return


def send_from():
    print('send_from')
    return

def send_off():
    print('send_off')
    return

def shutdown():
    print('shutdown')
    return

def handle():
    fd, msg = job_queue.get()
    cmd, tail = msg.split(' ',1)
    socket_handler[cmd](tail) if cmd in socket_hander \
            else fd.close()



if __name__ == '__main__':
    from threading import Thread
    from queue import Queue
    from sys import argv 
    from sys import stdin
    import select

    global login_queue
    job_queue = Queue()
    login_queue = Queue()

    MOTD = 'Hi'
    MAX_EVENTS=10
    n_workers=5

    server_handlers = {
            'LISTU': send_utsil,
            'TO': send_from,
            'MORF': send_ot,
            'BYE': send_off
            }

    stdin_handlers = {
            '/shutdown': shutdown
            }

    threads = []

    s = listen((argv[1],argv[2]))
    if not s:
        exit(1)

    t = Thread(target=login)
    t.start()
    threads.append(t)

    for i in range(n_workers):
        t = Thread(target=handle)
        t.start()
        threads.append(t)

    if not s:
        exit(1)

    epoll = select.epoll()
    epoll.register(s)
    epoll.register(stdin.fileno())
    while 1:
        l = epoll.poll(MAX_EVENTS)
        for fd, event in l:
            if fd == stdin.fileno():
                cmd = input().strip()
                stdin_handlers[cmd]() if cmd in stdin_handlers \
                        else print('invalid command')
            elif fd == s:
                connfd = s.accept()
                login_queue.put(confd)
                #add to login queue
            else:
                msg = read(fd)
                job_queue((fd, msg))

