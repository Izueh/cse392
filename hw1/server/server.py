import socket
from threading import Thread
from queue import Queue
from sys import argv
from sys import stdin
import select

def read(fd):
    msg = b''
    while not msg.endswith(b'\r\n\r\n'):
        msg += fd.recv(1)
        if len(msg) == 0:
            return None
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
    while(1):
        fd = login_queue.get()
        if fd == -1:
            thread_exit()
        try:
            buf = fd.recv(8)
            cmd = buf.split(b'\r\n\r\n')[0]
            if cmd == b'SHUTDOWN':
                thread_exit();
            if cmd != b'ME2U':
                raise Exception()
            fd.sendall(b'U2EM\r\n\r\n')
            buf = fd.recv(18)
            cmd,msg = buf.split(b' ')
            if cmd != b'IAM':
                raise Exception()
            name = msg.split(b'\r\n\r\n')[0]
            name = name.decode()
            with lock:
                if name in users:
                    fd.sendall(b'ETAKEN\r\n\r\n')
                    fd.close()
                    return
                fds[name] = fd
                users[fd] = name
            fd.sendall(b'MAI\r\n\r\n')
            fd.sendall(f'MOTD {MOTD}\r\n\r\n'.encode())
            epoll.register(fd.fileno(), select.EPOLLIN)
        except:
            fd.close()

def send_ot(readfd, msg):
    receiver_name = msg.split('\r\n\r\n')[0]
    with lock:
        if(receiver_name not in fds):
            print('Garbage')
            return
        fd = fds[receiver_name]
        sender_name = users[readfd]
        fd.sendall(f'OT {sender_name}\r\n\r\n'.encode())
    return

def send_utsil(readfd, msg):
    with lock:
        send_msg = 'UTSIL ' + ' '.join(users.keys())+'\r\n\r\n'
        readfd.sendall(send_msg.encode())
    return

def send_from(readfd, msg):
    receiver_name, msg = msg.split(' ', 1)
    with lock:
        if(receiver_name not in fds):
            readfd.sendall(f'EDNE {receiver_name}\r\n\r\n'.encode())
            return
        fd = fds[receiver_name]
        sender_name = users[readfd]
        fd.sendall(f'FROM {sender_name} {msg}'.encode()) #msg already has /r/n/r/n
    return

def send_off(readfd, msg):
    with lock:
        sender_name = users[readfd]
        readfd.sendall(b'EYB\r\n\r\n')
        del users[readfd]
        del fds[sender_name]
        for user in users:
            user.sendall(f'UOFF {sender_name}\r\n\r\n'.encode())
        epoll.unregister(readfd.fileno())
        readfd.close
    return

def shutdown():
    for fd in users:
        if cmd == b'SHUTDOWN':
            thread_exit();
        fd.close()
    login_queue.put(-1)
    for n in range(len(threads)-1):
        job_queue.put((-1,b''))
    for t in threads:
        t.join()
    exit(0)

def thread_exit():
    exit(0)

def list_user():
    print('Online Users:')
    for user in fds:
        print(user)

def display_help():
    print('''/users: Dumps a list of currently logged in users to stdout.
/shutdown: Cleanly shuts the server down by disconnecting all connected users, closing all open file descriptors, and freeing any allocated memory.''')

def handle():
    while(1):
        fd, msg = job_queue.get()
        if fd == -1:
            thread_exit()
        if(' ' in msg):
            cmd, tail = msg.split(' ',1)
        else:
            cmd = msg.split('\r\n\r\n')[0]
            tail = ''
        socket_handlers[cmd](readfd, tail) if cmd in socket_handlers \
                else fd.close()



if __name__ == '__main__':

    global login_queue
    global job_queue
    global users
    global fds
    global socket_handlers
    global epoll
    job_queue = Queue()
    login_queue = Queue()
    lock = threading.Lock()
    users = {}
    fds = {}

    MOTD = 'Hi'
    MAX_EVENTS=10
    n_workers=5

    socket_handlers = {
            'LISTU': send_utsil,
            'TO': send_from,
            'MORF': send_ot,
            'BYE': send_off
            }

    stdin_handlers = {
            '/shutdown': shutdown,
            '/users': list_user,
            '/help': display_help
            }

    threads = []

    s = listen((argv[1],argv[2]))
    if not s:
        print('error in listen')
        exit(1)

    t = Thread(target=login)
    t.start()
    threads.append(t)

    for i in range(n_workers):
        t = Thread(target=handle)
        t.start()
        threads.append(t)

    epoll = select.epoll()
    epoll.register(s.fileno())
    epoll.register(stdin.fileno(), select.EPOLLIN)
    connections = {}
    while 1:
        l = epoll.poll(10)
        for fd, event in l:
            if fd == stdin.fileno():
                print('stdinput')
                cmd = input().strip()
                stdin_handlers[cmd]() if cmd in stdin_handlers \
                        else print('invalid command')
            elif fd == s.fileno():
                (clientsocket, address) = s.accept()
                clientsocket.settimeout(5)
                #add to login queue
                login_queue.put(clientsocket)
                #add to connections list 
                connections[clientsocket.fileno()] = clientsocket;
            else:
                print('here')
                readfd = connections[fd]
                msg = read(readfd)
                if not msg:
                    readfd.close()
                    del connections[fd]
                    continue
                msg = msg.decode()
                if(len(msg) == 0):
                    #user left remove from the list and connections
                    print('left');
                job_queue.put((readfd, msg))

