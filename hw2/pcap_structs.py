from construct.core import  Struct
from construct import *
from structs import eth_header, ip_header

shb = Struct(
        block_type = Int32ub,
        block_len = Int32ub,
        bom = Int32ub,
        major_version = Int16ub,
        minor_version = Int16ub,
        section_len = Int64ub,
        block_len2 = Int32ub,
        idb = Struct(
            block_type = Int32ub,
            block_len = Int32ub,
            link_type = Int16ub,
            reserved = Int16ub,
            snap_len = Int32ub,
            block_len2 = Int32ub,
            ),
        )
epb_head = Struct(
        block_type = Int32ub,
        block_len = Int32ub,
        if_id = Int32ub,
        time = Int64ub,
        cap_len = Int32ub,
        len = Int32ub
        )
epb_foot = Int32ub

