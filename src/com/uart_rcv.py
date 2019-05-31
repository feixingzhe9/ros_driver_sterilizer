#!/usr/bin/env python
# coding=utf-8

import rospy
import time
import Queue
import uart_driver

#rcv_queue = None
rcv_queue = Queue.Queue()

def rcv_thread(tmp):
    global rcv_queue
    global ack_queue
    while not rospy.is_shutdown():
        read_data = uart_driver.com_rcv(20)
        if len(read_data) > 0:
            for i in read_data:
                rcv_queue.put(ord(i))
                print 'rcv: ', hex(ord(i))
            time.sleep(0.02)


def __main__():
    pass
