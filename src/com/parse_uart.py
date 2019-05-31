#!/usr/bin/env python
# coding=utf-8

import rospy
import Queue
import time
import uart_rcv
import uart_send
import protocol_param
ack_queue = Queue.Queue()


class RcvOpt(object):
    def __init__(self):
        self.start_flag_1 = False
        self.start_flag = False
        self.data_len = 0
        self.rcv_cnt = 0
        self.rcv_buf = []
        for i in range(0, protocol_param.FRAME_LEN_MAX):
            self.rcv_buf.append(0)
        #print self.rcv_buf


def cal_frame_sum(data, data_len):
    data_sum = 0
    for i in range(0, data_len):
       data_sum = data_sum + data[i]
       #print 'sum data: ', data[i]
    #print 'data_sum: ', data_sum
    return data_sum & 0x00ff

def protocol_proc_thread(tmp):
    data_tmp = 0
    rcv_com_opt = RcvOpt()
    #rcv_com_opt.__init__()
    while not rospy.is_shutdown():
        time.sleep(0.1)
        while not uart_rcv.rcv_queue.empty():
            data_tmp = uart_rcv.rcv_queue.get()
            rcv_com_opt.rcv_buf[rcv_com_opt.rcv_cnt] = data_tmp
            if rcv_com_opt.start_flag == True:
                if rcv_com_opt.rcv_cnt == 2:
                    rcv_com_opt.data_len = data_tmp
                    print 'rcv data len: ', rcv_com_opt.data_len

                if rcv_com_opt.rcv_cnt == rcv_com_opt.data_len + 2:
                    rcv_com_opt.start_flag = False
                    print "rcv cnt :", rcv_com_opt.rcv_cnt
                    rcv_com_opt.rcv_cnt = 0
                    print "rcv buf :", rcv_com_opt.rcv_buf
                    if cal_frame_sum(rcv_com_opt.rcv_buf, rcv_com_opt.data_len + 2) == rcv_com_opt.rcv_buf[rcv_com_opt.data_len + 2]:
                        proc_frame(rcv_com_opt.rcv_buf[3:], rcv_com_opt.data_len)
                        print "process frame protocol"
                    else:
                        print "frame check sum error !"
                        print "cal check sum is: ", cal_frame_sum(rcv_com_opt.rcv_buf, rcv_com_opt.data_len + 1)
                        print "get check sum is: ", rcv_com_opt.rcv_buf[rcv_com_opt.data_len + 2]
                        print "rcv buf :", rcv_com_opt.rcv_buf
                        rcv_com_opt.start_flag = False
                        rcv_com_opt.rcv_cnt = 0
                    break
            else:
                if rcv_com_opt.start_flag_1 == False:
                    if data_tmp == protocol_param.FRAME_HEADER_1:
                        rcv_com_opt.start_flag_1 = True
                        rcv_com_opt.rcv_cnt = 0
                else:
                    if data_tmp == protocol_param.FRAME_HEADER_2:
                        print "get HEADER"
                        rcv_com_opt.start_flag = True
                        rcv_com_opt.rcv_cnt = 1

            rcv_com_opt.rcv_cnt =  rcv_com_opt.rcv_cnt + 1
            if rcv_com_opt.rcv_cnt >= protocol_param.FRAME_LEN_MAX - 1:
                rcv_com_opt.start_flag = False
                rcv_com_opt.rcv_cnt = 0


class AckInfo(object):
    def __init__(self):
        self.cmd = 0
        self.proc_status = 0
        self.data = []
        for i in range(0, protocol_param.FRAME_LEN_MAX):
            self.data.append(0)
    def clear(self):
        self.cmd = 0
        self.protocol_type = 0
        for i in range(0, protocol_param.FRAME_LEN_MAX):
            self.data[i] = 0

def proc_frame(frame, frame_len):
    global ack_queue
    print "rcv frame: ", frame
    ack_info = AckInfo()
    cmd = frame[0]
    if frame_len >= protocol_param.FRAME_LEN_MAX - 4:
        return -1

    if cmd == protocol_param.PROTOCOL_CMD_START_STERILIZE:
        ack_info.clear()
        ack_info.cmd = protocol_param.PROTOCOL_CMD_START_STERILIZE
        ack_info.data[0] = frame[1]
        ack_info.data[1] = frame[2]
        ack_info.data[2] = frame[3]

        ack_queue.put(ack_info)

def __main__():
    pass
