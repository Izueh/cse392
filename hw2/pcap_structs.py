from construct.core import  Struct
from construct import *
from structs import eth_header, ip_header
SHB = {
        'block_type' : 0x0A0D0D0A,
        'block_len' : 28,
        'bom' : 0x1A2B3C4D,
        'major_version' : 1,
        'minor_version' : 0,
        'section_len' : 0,
        'block_len2' : 28
        }
IDB = {
        'block_type' : 0x00000001,
        'block_len' : 20,
        'link_type' : 1,
        'reserved' : 0,
        'snap_len' : 0,
        'block_len2' : 20
        }
shb = Struct(
        block_type = Int32ub,
        block_len = Int32ub,
        bom = Int32ub,
        major_version = Int16ub,
        minor_version = Int16ub,
        section_len = Int64ub,
        block_len2 = Int32ub,
        )
idb = Struct(
        block_type = Int32ub,
        block_len = Int32ub,
        link_type = Int16ub,
        reserved = Int16ub,
        snap_len = Int32ub,
        block_len2 = Int32ub,
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

