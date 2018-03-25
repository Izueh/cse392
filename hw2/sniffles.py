import argparse
from sys import argv
import socket
import signal
import hexdump
from structs import eth_header,ip_header


MAXLINE = 1500 


def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-o','--output',help='display a square of a given number',metavar='OUTPUT')
        parser.add_argument('-t','--timeout',help='Amount of time to capture for before quitting. If no\
                        time specified ^C must be sent to close program\
',metavar='TIMEOUT',type=int)
        parser.add_argument('-x','--hexdump', help='Print hexdump to stdout', action='store_true')
        parser.add_argument('-f','--filter',help='Filter for one specified protocol',metavar='{UDP,Ethernet,DNS,IP,TCP,TBD}')
        parser.add_argument('interface',help='interface to listen for traffic on', metavar='INTERFACE')
        return parser.parse_args(argv[1:])


def handler(signum, frame):
    global done
    done = True


if __name__ == '__main__':
    args = parse_args()

    done = False

    signal.signal(signal.SIGALRM, handler)
    #signal.signal(signal.SIGINT, handler)
    
    s = socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3))
    s.bind((args.interface, 0))
        
    if args.timeout:
        signal.alarm(args.timeout)

    while not done:
        #b = s.recv(MAXLINE)
        b = b'\xff\xff\xff\xff\xff\xff\x00PV\xc0\x00\x08\x08\x06\x00\x01\x08\x00\x06\x04\x00\x01\x00PV\xc0\x00\x08\xc0\xa8I\x01\x00\x00\x00\x00\x00\x00\xc0\xa8I\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        hexdump.dump(b)
        #eth = eth_header.parse(b)
        ip = ip_header.parse(b)

        print(f'\n{eth}')

