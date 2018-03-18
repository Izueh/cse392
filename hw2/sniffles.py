import argparse
from sys import argv
import socket
import signal
import hexdump


MAXLINE = 1024


def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-o','--output',help='display a square of a given number',metavar='OUTPUT')
        parser.add_argument('-t','--timeout',help='Amount of time to capture for before quitting. If no\
                        time specified ^C must be sent to close program\
',metavar='TIMEOUT',type=int)
        parser.add_argument('-x','--hexdump', help='Print hexdump to stdout', action='store_true')
        parser.add_argument('-f','--filter',help='Filter for one specified protocol',metavar='{UDP,Ethernet,DNS,IP,TCP,TBD}')
        parser.add_argument('interface',help='interface to listen for traffic on',metavar='INTERFACE')
        return parser.parse_args(argv)


def handler():
    done = True


if __name__ == '__main__':
    args = parse_args()

    done = False

    signal.signal(signal.SIGALRM, handler)
    signal.signal(signal.SIGINT, handler)
    
    s = socket.socket(socket.SOCK_RAW,socket.AF_PACKET,socket.htons(3))
    s.bind(args.interface, 0)
        
    b = b''

    if 'timeout' in args:
        signal.alarm(args.timeout)

    while not done:
        b+= s.recv(MAXLINE)

    if args.hexdump:
        hexdump.dump(b)
