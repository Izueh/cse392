from construct.core import Struct
from construct import Enum, Int16ub, Bytes, BytesInteger,BitStruct,BitsInteger,Int8ub,Nibble,FlagsEnum,Int32ub

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

ip_header = Struct(
        BitStruct(Int8ub,
            version=Nibble,
            header_len=Nibble,
            ),
        'service_type' / Int8ub,
        'total_len' / Int16ub,
        'indent' / Int16ub,)
"""
        fragment=BitStruct(Int16ub,
            FlagsEnum(BitsInteger(3),
                reserved_bit=0x1,
                no_fragment=0x2,
                more_fragment=0x4,
                ),
            fragment_offset=BitsInteger(16),
            ),
        ttl=Int8ub,
        protocol=Int8ub,
        ip_checksum=Int16ub,
        ip_src=Int32ub,
        ip_dest=Int32ub,
        )
"""




