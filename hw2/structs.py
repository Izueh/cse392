from construct.core import Struct
from construct import Enum, Int16ub, Bytes, BytesInteger,BitStruct,BitsInteger,Int8ub,Nibble,FlagsEnum,Int32ub, Octet, Short, Bytewise, this, RepeatUntil


def byte_to_string(obj, ctx):
        return obj.decode('utf-8')

eth_header = Struct(
        mac_dest=BytesInteger(6),
        mac_src=BytesInteger(6),
        types=Enum(Int16ub,
            IPv4=0x0800,
            ARP=0x0806,
            RARP=0x8035,
            X25=0x0805,
            IPX=0x8137,
            IPv6=0x86DD,
            ),
        )

ip_header = BitStruct(
        version=Nibble,
        header_len=Nibble,
        service_type = Bytewise(Int8ub),
        total_len = Bytewise(Int16ub),
        indent = Bytewise(Int16ub),
        flags = FlagsEnum(BitsInteger(3),
                reserved_bit=0x1,
                no_fragment=0x2,
                more_fragment=0x4,
                ),
        fragment_offset=BitsInteger(13),
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
        ip_src = Bytewise(Int32ub),
        ip_dest = Bytewise(Int32ub),
        optional = Bytewise(BytesInteger((this.header_len - 5) * 4)),
        )

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
    check_sum = Bytewise(Int16ub),
    urgent_point = Bytewise(Int16ub),
    )

udp_header = Struct(
    source_port = Int16ub,
    dest_port = Int16ub,
    length = Int16ub,
    check_sum = Int16ub,
    data = BytesInteger(this.length - 8),
    )



question_name = BitStruct(
         length = Octet,
         string = Bytewise(Bytes(this.length)) * byte_to_string,
)

question_struct = BitStruct(
        qname = Bytewise(RepeatUntil(lambda obj,lst,ctx: obj.length == 0, question_name)),
        qtype = Bytewise(Int16ub),
        qclass = Bytewise(Int16ub),
)

answer_struct = BitStruct(
        qname = Bytewise(RepeatUntil(lambda obj,lst,ctx: obj.length == 0, question_name)),
        qtye  = Bytewise(Int16ub),
        qclass = Bytewise(Int16ub),
        ttl = Bytewise(Int16ub),
        rdlength = Bytewise(Int16ub),
        rddata = Bytewise(Bytes(this.rdlength)),
)



dns_header = BitStruct(
    identification = Bytewise(Int16ub),
    QR = BitsInteger(1),
    opcode = Nibble,
    flags = FlagsEnum(Nibble,
        AA = 0x1,
        TC = 0x2,
        RD = 0x4,
        RA = 0x8,
        ),
    zero = BitsInteger(3),
    rcode = Nibble,
    question_num = Bytewise(Int16ub),
    answer_num = Bytewise(Int16ub),
    authority_num = Bytewise(Int16ub),
    addition_num = Bytewise(Int16ub),
    questions = Bytewise(question_struct[this.question_num]),
    answers = Bytewise(answer_struct[this.answer_num]),
    )
