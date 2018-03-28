from construct import *
from construct.lib import *

# Functions for parsing (decoding) the read bytes into appropiate format
MacAddress = ExprAdapter(Byte[6],
         decoder = lambda obj,ctx: ":".join("%02x" % byte for byte in obj),
         encoder = obj_-1
        )

IPAddress = ExprAdapter(Byte[4],
        decoder = lambda obj,ctx: f'{obj[0]}.{obj[1]}.{obj[2]}.{obj[3]}',
        encoder = obj_-1)

QName = ExprAdapter(RepeatUntil(len_(obj_)==0, PascalString(Byte, "ascii")),
        decoder = lambda obj,ctx:  ".".join(obj[:-1]),
        encoder = obj_-1)


aname_struct = Struct(
    length = Peek(Int8ub),
    pointer = Computed(this.length & 0XC0 == 0xC0),
    label = IfThenElse(this.pointer, Int16ub, PascalString(Byte, "ascii")),
)

AName = ExprAdapter(RepeatUntil(obj_.pointer | (obj_.length==0) , aname_struct),
      decoder= lambda obj,ctx: obj[0].label if obj[0].pointer else '.'.join((o.label for o in obj[:-1])),
      encoder=obj_-1)

# Ethernet Header
eth_header = Struct(
        mac_dest = MacAddress,
        mac_src = MacAddress,
        types = Enum(Int16ub,
            IPv4=0x0800,
            ARP=0x0806,
            RARP=0x8035,
            X25=0x0805,
            IPX=0x8137,
            IPv6=0x86DD,
            ),
        )

# ARP Header
arp_header = Struct(
        hware_type = Enum(Int16ub,
            EHTERNET=0X1,
            HYPERCHNNEL=0x8,
            ULTRALINK=0xD,
            FRAME_RELAY=0XF,
            IEEE1394=0x18,
            ARPSEC=0x1E,
            IPSEC_TUNNEL=0x1F,
            INFINIBAND=0x20,
                ),
        protocol_type = Enum(Int16ub,
            IP=0x800,
                ),
        hward_addr_len = Int8ub,
        proto_addr_len = Int8ub,
        opcode = Enum(Int16ub,
            REQUEST=0x1,
            REPLY=0x2,
            REQUEST_REVERSE=0x3,
            REPLY_REVERSE=0x4,
            ARP_NAK=0xA,
            ),
        src_hward_addr = Bytes(this.hward_addr_len),
        src_proto_addr = Bytes(this.proto_addr_len),
        dest_hward_addr = Bytes(this.hward_addr_len),
        dest_proto_addr = Bytes(this.proto_addr_len),
    )



# IPv4 Header
ip_header = BitStruct(
        version = Nibble,
        header_len = Nibble,
        service_type = Bytewise(Int8ub),
        total_len = Bytewise(Int16ub),
        indent = Bytewise(Int16ub),
        flags = FlagsEnum(BitsInteger(3),
            RESERVED_BIT=0x1,
            NO_FRAGMENTS=0x2,
            MORE_FRAGMENTS=0x4,
            ),
        fragment_offset = BitsInteger(13),
        ttl = Bytewise(Int8ub),
        protocol = Enum(Bytewise(Int8ub),
                ICMP=0x1,
                TCP=0x6,
                UDP=0x11,
                PPTP=0x47,
                AH=0x33,
                EGP=0x8,
                GGP=0x3,
                HMP=0x14,
                IGMP=0x58,
                RVD=0x42,
                PUP=0xC,
                RDP=0x1B,
                RSVP=0x2E,
                ),
        ip_checksum = Bytewise(Int16ub),
        ip_src = IPAddress,
        ip_dest = IPAddress,
        optional = Bytewise(Bytes((this.header_len - 5) * 4)),
        )

# TCP Header
tcp_header = BitStruct(
    source_port = Bytewise(Int16ub),
    dest_port = Bytewise(Int16ub),
    seq_num = Bytewise(Int32ub),
    ack_num = Bytewise(Int32ub),
    data_offset = Nibble,
    reserved = BitsInteger(3),
    control_flags = FlagsEnum(BitsInteger(9),
                Nonce=0x1,
                CWR=0x2,
                ECN_Echo=0x4,
                Urgent=0x8,
                Ack=0x10,
                Push=0x20,
                Reset=0x40,
                Sync=0x80,
                Fin=0x100,
                ),
    window_size = Bytewise(Int16ub),
    checksum = Bytewise(Int16ub),
    urgent_point = Bytewise(Int16ub),
    )

# UDP Header
udp_header = Struct(
    source_port = Int16ub,
    dest_port = Int16ub,
    length = Int16ub,
    checksum = Int16ub,
    data = Bytes(this.length - 8),
    )

# DNS
# Question/Answer Type Enum
QTypeEnum = Enum(Int16ub,
                 A=0x1,
                 NS=0x2,
                 MD=0x3,
                 MF=0x4,
                 CNAME=0x5,
                 SOA=0x6,
                 MB=0x7,
                 MG=0x8,
                 MR=0x9,
                 NULL=0xA,
                 WKS=0xB,
                 PTR=0xC,
                 HINFO=0xD,
                 MINFO=0xE,
                 MX=0xF,
                 TXT=0x10,
                    )
# Question/Answer Class Enum
QClassEnum = Enum(Int16ub,
                  IN=0x1,
                  CS=0x2,
                  CH=0x3,
                  HS=0x4,
                 )

# DNS Questoin Struct
question_struct = Struct(
        qname = QName,
        qtype = QTypeEnum,
        qclass = QClassEnum,
)

# DNS Answer Struct
answer_struct = Struct(
        qname = AName,
        qtye  = QTypeEnum,
        qclass = QClassEnum,
        ttl = Int32sb,
        rdlength = Int16ub,
        rddata = Bytes(this.rdlength),
)

dns_flag = BitStruct(
    QR = BitsInteger(1),
    opcode = Nibble,
    flags = FlagsEnum(Nibble,
        AA=0x1,
        TC=0x2,
        RD=0x4,
        RA=0x8,
        ),
    zero = BitsInteger(3),
    rcode = Nibble,
)

# DNS Header 
dns_header = Struct(
    identification = Int16ub,
    flags = Int16ub,
    question_num = Int16ub,
    answer_num = Int16ub,
    authority_num = Int16ub,
    addition_num = Int16ub,
    questions = question_struct[this.question_num],
    answers = answer_struct[this.answer_num],
#    authority = Bytewise(answer_struct[this.authority_num]),
#    addition = Bytewise(answer_struct[this.addition_num]),
    )
