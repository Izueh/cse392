import argparse
from sys import argv
import socket
import signal
import hexdump
from structs import eth_header,ip_header, tcp_header, udp_header


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
        b = s.recv(MAXLINE)
        eth = eth_header.parse(b)
        if eth.types == 'IPv4':
            ip = ip_header.parse(b[14:])
            ip_eth_len = (ip.header_len * 4) + 14
            if ip.protocol == 'TCP':
                tcp = tcp_header.parse(b[ip_eth_len:])
            elif ip.protocol == 'UDP':
                udp = udp_header.parse(b[ip_eth_len:])
                print(b)
                print(hexdump.dump(b))
                print(udp)

