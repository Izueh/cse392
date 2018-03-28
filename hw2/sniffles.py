import argparse
from sys import argv
import socket
import signal
import hexdump
from structs import eth_header,ip_header, tcp_header, udp_header, dns_header, question_struct, arp_header, AName, answer_struct

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


    b = b'\xae\xa2\x81\x80\x00\x01\x00\x03\x00\x00\x00\x01\x03\x77\x77\x77\x05\x67\x6d\x61\x69\x6c\x03\x63\x6f\x6d\x00\x00\x01\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x06\xc1\x00\x0e\x04\x6d\x61\x69\x6c\x06\x67\x6f\x6f\x67\x6c\x65\xc0\x16\xc0\x2b\x00\x05\x00\x01\x00\x02\x7a\xc3\x00\x0f\x0a\x67\x6f\x6f\x67\x6c\x65\x6d\x61\x69\x6c\x01\x6c\xc0\x30\xc0\x45\x00\x01\x00\x01\x00\x00\x00\xc2\x00\x04\xac\xd9\x06\xc5\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00'
    print(dns_header.parse(b))

"""
    while not done:
        b = s.recv(MAXLINE)
        eth = eth_header.parse(b)
        print(f'ETH(MacDest={eth.mac_dest}, MacSrc={eth.mac_src}, Type={eth.types})\n')
        if eth.types == 'IPv4':
            ip = ip_header.parse(b[14:])
            ip_eth_len = (ip.header_len * 4) + 14
            print(f'''IPv4(FSrcIP={ip.ip_src}, DestIP={ip.ip_dest}, flags={ip.flags}, FragmentOffset={ip.fragment_offset}, \n
                    TTL={ip.ttl}, Protocol={ip.protocol}, CheckSum={ip.ip_checksum}, Optional={ip.optional}, Version={ip.version}, \n
                    HeadLen={ip.header_len}, ServiceType={ip.service_type}, TotalLen={ip.total_len} \n''')
            if ip.protocol == 'TCP':
                tcp = tcp_header.parse(b[ip_eth_len:])
                print(f'''TCP(SrcPort={tcp.source_port}, DestPort={tcp.dest_port}, SeqNum={tcp.seq_num}, AckNum={tcp.ack_num},
                        DataOff={tcp.data_offset}, Flags={tcp.control_flags}, WinSize={tcp.window_size},
                        ChkSum={tcp.checksum}, UrgentPtr={tcp.urgent_point})''')
                if(tcp.dest_port == 53 or tcp.source_port == 53):
                    dns = dns_header.parse(tcp.data)
                    print(dns)
            elif ip.protocol == 'UDP':
                udp = udp_header.parse(b[ip_eth_len:])
                print(f'UDP(SrcPort={udp.source_port}, DestPort={udp.dest_port}, Length={udp.length}, Checksum={udp.checksum})\n')
                if(udp.dest_port == 53 or udp.source_port == 53):
                    dns = dns_header.parse(udp.data)
                    print(dns)
        elif eth.types == 'ARP':
            arp = arp_header.parse(b[14:])
            print(arp)
        print('-----------------------------------------------')
"""
