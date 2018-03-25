from construct.core import Struct
from construct import Enum, Int16ub, Bytes, BytesInteger,BitStruct,BitsInteger,Int8ub,Nibble,FlagsEnum,Int32ub, Octet, Short, Bytewise

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
        )


