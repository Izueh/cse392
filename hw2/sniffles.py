import argparse
from sys import argv
import socket
import signal
import hexdump
from structs import eth_header,ip_header, tcp_header, udp_header, dns_header, question_struct


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

    dns = dns_header.parse(b'\xdb\x42\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77\x0c\x6e\x6f\x72\x74\x68\x65\x61\x73\x74\x65\x72\x6e\x03\x65\x64\x75\x00\x00\x01\x00\x01')
  #  dns = question_struct.parse(b'\x03\x77\x77\x77\x0c\x6e\x6f\x72\x74\x68\x65\x61\x73\x74\x65\x72\x6e\x03\x65\x64\x75\x00\x00\x01\x00\x01')
    print(dns)
'''
    while not done:
        b = s.recv(MAXLINE)
        eth = eth_header.parse(b)
        if eth.types == 'IPv4':
            ip = ip_header.parse(b[14:])
            ip_eth_len = (ip.header_len * 4) + 14
            if ip.protocol == 'TCP':
                tcp = tcp_header.parse(b[ip_eth_len:])
                if(tcp.dest_port == 52):
                    dns = dns_header(tcp.data)
            elif ip.protocol == 'UDP':
                udp = udp_header.parse(b[ip_eth_len:])
                if(udp.dest_port == 52):
                    dns = dns_header(udp.data)
                print(b)
                print(hexdump.dump(b))
                print(udp)
'''
