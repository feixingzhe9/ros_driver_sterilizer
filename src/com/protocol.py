
#!/usr/bin/env python
# coding=utf-8

import rospy
import time
import Queue
import sys
import json
import uart_driver
import uart_send
import parse_uart
import protocol_param
from std_msgs.msg import String


pub_to_mission = None
sub_from_mission = None
_is_sterilezing = False

reload(sys)
sys.setdefaultencoding('utf-8')

file_ = sys._getframe().f_code.co_filename
func_ = sys._getframe().f_code.co_name


def mission_callback(data):
    cmd = json.loads(data.data)
    rospy.loginfo("receive mission cmd : %s", data.data)
    if cmd.has_key('pub_name'):
        task_cmd = cmd['pub_name']
        if cmd['pub_name'] == "start_sterilize":
            start_sterilize()
            pass
    else:
        rospy.logwarn("incoming data illegal %s", str(cmd))
        return


def ack_start_sterilize(result):
    msg = {'sub_name': 'start_sterilize', 'result': result}
    pub_to_mission.publish(json.dumps(msg))

def init():
    global sub_from_mission
    global pub_to_mission
    sub_from_mission = rospy.Subscriber("sterilizer_ctrl", String, mission_callback)
    pub_to_mission = rospy.Publisher("sterilizer_ctrl_ack", String, queue_size=1)

def de_init():
    global sub_from_mission
    global pub_to_mission
    sub_from_mission.unregister()
    pub_to_mission.unregister()

def set_sterilizer_up():
    data_len = 5 
    send_data = uart_send.SendData()
    send_data.clear()
    send_data.data[0] = protocol_param.FRAME_HEADER_1
    send_data.data[1] = protocol_param.FRAME_HEADER_2
    send_data.data[2] = data_len
    send_data.data[3] = protocol_param.PROTOCOL_CMD_START_STERILIZE
    send_data.data[4] = 0x4f
    send_data.data[5] = 0x4b
    send_data.data[6] = 0
    send_data.data[7] = parse_uart.cal_frame_sum(send_data.data, data_len + 2)

    send_data.len = data_len + 3
    uart_send.send_queue.queue.clear()  #clear send queue
    uart_send.send_queue.put(send_data)

    cnt = 0
    while 1:
        if not parse_uart.ack_queue.empty():
            ack = parse_uart.ack_queue.get()
            if ack.cmd == protocol_param.PROTOCOL_CMD_START_STERILIZE and ack.data[0]  == 0x4f and ack.data[1]  == 0x4b and ack.data[2]  == 0:
                print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, " get right ack"
                uart_send.send_queue.queue.clear()  #clear send queue cause we get right ack and do not need to send anything
                break
        time.sleep(0.5)
        cnt = cnt + 1
        if cnt % 5 == 4:
            uart_send.send_queue.put(send_data)
        if cnt > 5 * 8:
            print ''
            print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, "Error: sterilezer up failed ! !"
            return -1



def ack_sterileze_done():
    data_len = 5
    send_data = uart_send.SendData()
    send_data.clear()
    send_data.data[0] = protocol_param.FRAME_HEADER_1
    send_data.data[1] = protocol_param.FRAME_HEADER_2
    send_data.data[2] = data_len
    send_data.data[3] = protocol_param.PROTOCOL_CMD_STERILIZE_DONE
    send_data.data[4] = 0
    send_data.data[5] = 0
    send_data.data[6] = 0
    send_data.data[7] = parse_uart.cal_frame_sum(send_data.data, data_len + 2)

    send_data.len = data_len + 3
    uart_send.send_queue.put(send_data)

def start_sterilize():
    global _is_sterilezing
    if not _is_sterilezing:
        data_len = 5
        send_data = uart_send.SendData()
        send_data.clear()
        send_data.data[0] = protocol_param.FRAME_HEADER_1
        send_data.data[1] = protocol_param.FRAME_HEADER_2
        send_data.data[2] = data_len
        send_data.data[3] = protocol_param.PROTOCOL_CMD_START_STERILIZE
        send_data.data[4] = 0
        send_data.data[5] = 0
        send_data.data[6] = 0
        send_data.data[7] = parse_uart.cal_frame_sum(send_data.data, data_len + 2)

        send_data.len = data_len + 3
        uart_send.send_queue.queue.clear()  #clear send queue
        uart_send.send_queue.put(send_data)

        cnt = 0
        while 1:
            if not parse_uart.ack_queue.empty():
                ack = parse_uart.ack_queue.get()
                if ack.cmd == protocol_param.PROTOCOL_CMD_START_STERILIZE and ack.data[0]  == 0 and ack.data[1]  == 0 and ack.data[2]  == 0:
                    print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, " get right ack"
                    uart_send.send_queue.queue.clear()  #clear send queue cause we get right ack and do not need to send anything
                    ack_start_sterilize('start_ok')
                    break
            time.sleep(0.5)
            cnt = cnt + 1
            if cnt % 5 == 4:
                uart_send.send_queue.put(send_data)
            if cnt > 5 * 3:
                print ''
                print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, "Error: sterilize failed ! !"
                ack_start_sterilize('start_err')
                return -1

        _is_sterilezing = True

        time.sleep(290) # 5 minite
        while 1:
            if not parse_uart.ack_queue.empty():
                ack = parse_uart.ack_queue.get()
                if ack.cmd == protocol_param.PROTOCOL_CMD_STERILIZE_DONE and ack.data[0]  == 0 and ack.data[1]  == 0 and ack.data[2]  == 0:
                    print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, " sterilization done"
                    uart_send.send_queue.queue.clear()  #clear send queue cause we get right ack and do not need to send anything
                    ack_sterileze_done()
                    ack_start_sterilize('exec_ok')
                    _is_sterilezing = False
                    break
            time.sleep(1)
            cnt = cnt + 1
            if cnt % 5 == 4:
                pass
                #uart_send.send_queue.put(send_data)
            if cnt > 5 * 8:
                print ''
                print file_, sys._getframe().f_code.co_name, sys._getframe().f_lineno, "Error: sterilize failed ! !"
                ack_start_sterilize('exec_err')
                return -1
