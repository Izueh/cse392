import argparse
from sys import argv
import socket
import signal
import select
import hexdump
import fcntl
import time
import os
from structs import eth_header,ip_header, tcp_header, udp_header, dns_header, question_struct, arp_header, AName, answer_struct
from pcap_structs import shb, epb_head, epb_foot

def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-o','--output',help='display a square of a given number',metavar='OUTPUT')
        parser.add_argument('-t','--timeout',help='Amount of time to capture for before quitting. If no\
o                        time specified ^C must be sent to close program\
',metavar='TIMEOUT',type=int)
        parser.add_argument('-x','--hexdump', help='Print hexdump to stdout', action='store_true')
        parser.add_argument('-f','--filter',help='Filter for one specified protocol',metavar='{UDP,Ethernet,DNS,IP,TCP,TBD}')
        parser.add_argument('interface',help='interface to listen for traffic on', metavar='INTERFACE')
        return parser.parse_args(argv[1:])


def handler(signum, frame):
    global done
    done = True

def get_flags(flags):
    return ' '.join(filter(lambda x: flags[x] and x!='_flagsenum',flags.keys()))

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
    addition_num = {dns.addition_num}) \n''')

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
    print('\n==================================================\n')


def printARP(arp):
    print(f'''(ARP Hardware Type={arp.hware_type}, Protocol Type={arp.protocol_type}, Hardware Addr Len={arp.hware_addr_len},
    Protocol Addr Len = {arp.proto_addr_len}, opcode = {arp.opcode}, Src Hwd Addr={arp.src_hware_addr},
    Src Proto Addr={arp.src_proto_addr}, Dest Hwd Addr={arp.dest_hware_addr}, Dest Proto Addr={arp.dest_proto_addr}\n''')

def write_packet(b, f):
    original_len = len(b)
    padding = 4 - len(b) % 4 if len(b) % 4 else 0
    b += (b'\x00' * padding)
    a = {
            'block_type' : 0x0A0D0D0A,
            'block_len' : 28,
            'bom' : 0x1A2B3C4D,
            'major_version' : 1,
            'minor_version' : 0,
            'section_len' : 0,
            'block_len2' : 28,
            'idb' : {
                'block_type' : 0x00000001,
                'block_len' : 20,
                'link_type' : 1,
                'reserved' : 0,
                'snap_len' : 0,
                'block_len2' : 20
                }
            }
    c = {
            'block_type' : 6,
            'block_len' : len(b) + 32,
            'if_id' : 0,
            'time' : int(round(time.time()*1e6)),
            'cap_len' : original_len,
            'len' : original_len,
            }
    f.write(shb.build(a))
    f.write(epb_head.build(c))
    f.write(b)
    f.write(epb_foot.build(c['block_len']))

if __name__ == '__main__':
    args = parse_args()

    done = False

    signal.signal(signal.SIGALRM, handler)
    signal.signal(signal.SIGINT, handler)

    s = socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3))
    if_name = args.interface.encode('utf-8')
    ifr = if_name + b'\x00'*(32-len(if_name))
    ifs = fcntl.ioctl(s,0x8921,ifr)
    mtu = int.from_bytes(ifs[16:18], byteorder='little')
    MAXLINE = mtu if args.interface != 'lo' else 2**16 

    r,w = os.pipe()
    os.set_blocking(w,False)
    
    signal.set_wakeup_fd(w)
    s.bind((args.interface, 0))

    if args.timeout:
        signal.alarm(args.timeout)

    f = open(args.output,'wb') if args.output else None

    packets = 0

    while not done:
        read, _, _ = select.select([s,r],[],[])
        if s in read:
            b = s.recv(MAXLINE)
        else:
            continue

        packets += 1
        #hexdump raw bytes
        if args.hexdump:
                hexdump.hexdump(b)

        #parse specified protocol
        eth = eth_header.parse(b)
        if args.filter == 'Ethernet':
            print(f'ETH(MacDest={eth.mac_dest}, MacSrc={eth.mac_src}, Type={eth.types})\n')
        if eth.types == 'IPv4':
            ip = ip_header.parse(b[14:])
            ip_eth_len = (ip.header_len * 4) + 14
            if args.filter == 'IP':
                printIP(ip)
            if ip.protocol == 'TCP':
                tcp = tcp_header.parse(b[ip_eth_len:])
                if args.filter == 'TCP':
                    printTCP(tcp)
                if (tcp.dest_port == 53 or tcp.source_port == 53) and (args.filter == 'DNS'):
                    dns = dns_header.parse(tcp.data)
                    printDNS(dns)
            elif ip.protocol == 'UDP':
                udp = udp_header.parse(b[ip_eth_len:])
                if args.filter == 'UDP':
                    printUDP(udp)
                if(udp.dest_port == 53 or udp.source_port == 53) and (args.filter == 'DNS'):
                    dns = dns_header.parse(udp.data)
                    printDNS(dns)
        elif eth.types == 'ARP' and args.filter == 'ARP':
            arp = arp_header.parse(b[14:])
            printARP(arp)

        #write pcap file
        if f:
            write_packet(b,f)

    if f:
        f.close()

    print(f'{packets} packets read')

