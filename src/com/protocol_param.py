#!/usr/bin/env python
# coding=utf-8


FRAME_HEADER_1 = 0xAA
FRAME_HEADER_2 = 0x55

FRAME_LEN_MAX = 64

PROTOCOL_CMD_START_STERILIZE = 0x11
PROTOCOL_CMD_STERILIZE_DONE = 0x12

def is_protocol_cmd(cmd):
    if cmd == PROTOCOL_CMD_START_STERILIZE:
        return True
    return False
