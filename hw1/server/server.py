import socket
from threading import Thread,Lock
from queue import Queue
from sys import argv
from sys import stdin
from argparse import ArgumentParser
import select


def printv(s):
    if args.v:
        print(f'\x1B[1;34m{s}\x1B[0m')

def read(fd):
    msg = b''
    try:
        while not msg.endswith(b'\r\n\r\n'):
            msg += fd.recv(1)
            if len(msg) == 0:
                return None
    except (ConnectionResetError, socket.timeout) as e:
        return None

    printv(f"{msg.decode('utf-8')[:-4]}")
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
            buf = read(fd)
            cmd = buf.split(b'\r\n\r\n')[0]
            if cmd == b'SHUTDOWN':
                thread_exit();
            if cmd != b'ME2U':
                raise Exception()
            fd.sendall(b'U2EM\r\n\r\n')
            printv("U2EM")
            buf = read(fd)
            cmd,msg = buf.split(b' ')
            if cmd != b'IAM':
                raise Exception()
            name = msg.split(b'\r\n\r\n')[0]
            name = name.decode()
            with lock:
                if name in users:
                    fd.sendall(b'ETAKEN\r\n\r\n')
                    printv("ETAKEN")
                    fd.close()
                    return
                fds[name] = fd
                users[fd] = name
            fd.sendall(b'MAI\r\n\r\n')
            printv("MAI")
            fd.sendall(f'MOTD {MOTD}\r\n\r\n'.encode())
            printv(f"MOTD {MOTD}")
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
    printv(f"OT {sender_name}")
    return

def send_utsil(readfd, msg):
    with lock:
        ul = ' '.join(fds.keys())
        send_msg = f'UTSIL {ul}\r\n\r\n' 
        readfd.sendall(send_msg.encode())
    printv(f"{send_msg[:-4]}")
    return

def send_from(readfd, msg):
    receiver_name, msg = msg.split(' ', 1)
    with lock:
        if(receiver_name not in fds):
            readfd.sendall(f'EDNE {receiver_name}\r\n\r\n'.encode())
            printv(f"EDNE {receiver_name}")
            return
        fd = fds[receiver_name]
        sender_name = users[readfd]
        fd.sendall(f'FROM {sender_name} {msg}'.encode()) #msg already has /r/n/r/n
        printv(f"FROM {sender_name} {msg}")
    return

def send_off(readfd, msg):
    with lock:
        sender_name = users[readfd]
        readfd.sendall(b'EYB\r\n\r\n')
        del users[readfd]
        del fds[sender_name]
        del connections[readfd.fileno()]
        for user in users:
            user.sendall(f'UOFF {sender_name}\r\n\r\n'.encode())
            printv(f"FROM {sender_name} {msg}")
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
        if cmd in socket_handlers:
            socket_handlers[cmd](readfd, tail) 
        else:
            epoll.unregister(fd.fileno())
            fd.close()




if __name__ == '__main__':

    global login_queue
    global job_queue
    global users
    global fds
    global socket_handlers
    global epoll
    job_queue = Queue()
    login_queue = Queue()
    lock = Lock()
    users = {}
    fds = {}

    parser = ArgumentParser(description="ME2U Server")
    parser.add_argument('-v',action='store_true',help='Logs client server communication')
    parser.add_argument('port',metavar='PORT', help='Port number to listen on',default='8080')
    parser.add_argument('n', metavar='NUM WORKERS',help='Number of worker threads to spawn', default=5, type=int)
    parser.add_argument('motd', metavar='MOTD',help='Message of the Day to display', default='Welcome')
    parser.add_argument('addr', metavar='ADDR',nargs='?',help='Address to listen on',default='localhost')
    args = parser.parse_args()

    MOTD = args.motd
    MAX_EVENTS=10
    n_workers= args.n

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

    s = listen((args.addr,args.port))
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
            if fd == s.fileno():
                (clientsocket, address) = s.accept()
                clientsocket.settimeout(5)
                #add to login queue
                login_queue.put(clientsocket)
                #add to connections list 
                connections[clientsocket.fileno()] = clientsocket;
            elif event & select.EPOLLIN:
                if fd == stdin.fileno():
                    cmd = input().strip()
                    stdin_handlers[cmd]() if cmd in stdin_handlers \
                            else print('invalid command')
                else:
                    readfd = connections[fd]
                    msg = read(readfd)
                    if not msg:
                        with lock:
                            user = users[readfd]
                            del fds[user]
                            del users[readfd]
                            readfd.close()
                            del connections[fd]
                        continue
                    msg = msg.decode()
                    job_queue.put((readfd, msg))

