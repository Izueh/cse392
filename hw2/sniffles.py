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

def get_flags(flags):
    flags = ''
    for f in ip.flags:
        if ip.flags[f] and f != '_flagsenum':
            flags += f'{f} '
    return flags

def printIP(ip):
    print(f'''IPv4(Protocol={ip.protocol}, FSrcIP={ip.ip_src}, DestIP={ip.ip_dest}, flags={get_flags(ip.flags)},
     FragmentOffset={ip.fragment_offset}, TTL={ip.ttl}, CheckSum={ip.ip_checksum},Version={ip.version},
     HeadLen={ip.header_len}, ServiceType={ip.service_type}, TotalLen={ip.total_len}, Optional={ip.optional} )\n''')

def printTCP(tcp):
    print(f'''TCP(SrcPort={tcp.source_port}, DestPort={tcp.dest_port}, SeqNum={tcp.seq_num}, AckNum={tcp.ack_num},
    DataOff={tcp.data_offset}, Flags={get_flags(tcp.control_flags)}, WinSize={tcp.window_size},
    ChkSum={tcp.checksum}, UrgentPtr={tcp.urgent_point})''')

def printUDP(udp):
    print(f'UDP(SrcPort={udp.source_port}, DestPort={udp.dest_port}, Length={udp.length}, Checksum={udp.checksum})\n')

def printDNS(dns):
    print(f'''DNS(id={dns.identification}, QR={dns.flags.QR}, OPCode={dns.flags.opcode}, flags={get_flags(dns.flags.flags)},
    rcode={dns.flags.rcode}, question_num={dns.question_num}, answer_num={dns.answer_num}, additional_num={dns.authority_num},
    addition_num = {dns.addition_num} \n''')

    print('Questions:')
    for que in dns.questions:
        print(f'\tQname={que.qname}, Qtype={que.qtype}, Qclass={que.qclass}')

    print('Answers:')
    for ans in dns.answers:
        print(f'''\tAname={ans.aname}, Qtype={ans.atype}, Qclass={ans.aclass},
        TTL={ans.ttl}, RDLength={ans.rdlength}, RDData={ans.rddata}''')

    print('Authority:')
    for ans in dns.authority:
        print(f'''\tAname={ans.aname}, Qtype={ans.atype}, Qclass={ans.aclass},
        TTL={ans.ttl}, RDLength={ans.rdlength}, RDData={ans.rddata}''')

    print('Addition:')
    for ans in dns.addition:
        print(f'''\tAname={ans.aname}, Qtype={ans.atype}, Qclass={ans.aclass},
        TTL={ans.ttl}, RDLength={ans.rdlength}, RDData={ans.rddata}''')

def printARP(arp):
    print(f'''(ARP Hardware Type={arp.hward_type}, Protocol Type={arp.protocol_type}, Hardware Addr Len={arp.hward_addr_len},
    Protocol Addr Len = {arp.protocol_addr_len}, opcode = {arp.opcode}, Src Hwd Addr={arp.src_hward_addr},
    Src Proto Addr={arp.src_proto_addr}, Dest Hwd Addr={arp.dest_hward_addr}, Dest Proto Addr={arp.dest_proto_addr}\n''')


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
        print(f'ETH(MacDest={eth.mac_dest}, MacSrc={eth.mac_src}, Type={eth.types})\n')
        if eth.types == 'IPv4':
            ip = ip_header.parse(b[14:])
            ip_eth_len = (ip.header_len * 4) + 14
            printIP(ip)
            if ip.protocol == 'TCP':
                tcp = tcp_header.parse(b[ip_eth_len:])
                printTCP(tcp)
                if(tcp.dest_port == 53 or tcp.source_port == 53):
                    dns = dns_header.parse(tcp.data)
                    printDNS(dns)
            elif ip.protocol == 'UDP':
                udp = udp_header.parse(b[ip_eth_len:])
                printUDP(udp)
                if(udp.dest_port == 53 or udp.source_port == 53):
                    dns = dns_header.parse(udp.data)
                    printDNS(dns)
        elif eth.types == 'ARP':
            arp = arp_header.parse(b[14:])
            print(arp)
        print('-----------------------------------------------------------------------------')
