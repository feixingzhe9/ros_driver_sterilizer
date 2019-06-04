#!/usr/bin/env python
# coding=utf-8

import rospy
import threading
#import Queue
import sys
#import numpy as np
import time
#import json
from com import uart_driver
from com import uart_rcv
from com import uart_send
from com import parse_uart
from com import protocol
#from com import protocol_param

def main():

    rospy.init_node("driver_sterilizer", anonymous=True)

    uart_driver.open_com()
    thread_send = threading.Thread(target = uart_send.send_thread, args = (0,))
    thread_rcv = threading.Thread(target = uart_rcv.rcv_thread, args = (0,))
    thread_protocol_proc = threading.Thread(target = parse_uart.protocol_proc_thread, args = (0,))

    thread_send.start()
    thread_rcv.start()
    thread_protocol_proc.start()
    #time.sleep(1)
    #protocol.set_sterilizer_up()
    time.sleep(5)
    protocol.start_sterilize()
    rospy.spin()

if __name__ == "__main__":
    try:
        main()
    except Exception: #rospy.ROSInterruptException:
        rospy.logerr(sys.exc_info())
        rospy.loginfo("lost connect")
        exit(1)
