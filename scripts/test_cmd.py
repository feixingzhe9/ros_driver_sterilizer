#!/usr/bin/env python
# coding:utf-8

import sys
import rospy
import time
import json
from std_msgs.msg import String


def post_mission_cmd(pub, cmd):
    msg = {}
    msg['pub_name'] = cmd
    pub.publish(json.dumps(msg))

if __name__ == "__main__":
    rospy.init_node("fake_cmd", anonymous=True)
    pub_mission = rospy.Publisher("sterilizer_ctrl", String, queue_size=10)

    time.sleep(1)
    if sys.argv[1] == '0':
        post_mission_cmd(pub_mission, "start_sterilize")


