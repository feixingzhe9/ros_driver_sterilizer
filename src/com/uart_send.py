#!/usr/bin/env python
# coding=utf-8

import rospy
import time
import uart_driver
import Queue
import protocol_param

send_queue = Queue.Queue()

class SendData(object):
    def __init__(self):
        self.len = 0
        self.data = []
        for i in range(0, protocol_param.FRAME_LEN_MAX):
            self.data.append(0)
    def clear(self):
        for i in range(0, protocol_param.FRAME_LEN_MAX):
            self.data[i] = 0

def send_thread(tmp):
    while not rospy.is_shutdown():
        if not send_queue.empty():
            data = send_queue.get()
            if data is not None:
                print 'send_len: ', data.len
                values = bytearray(data.data[0:data.len])
                uart_driver.com_send(values)
        time.sleep(0.05)
