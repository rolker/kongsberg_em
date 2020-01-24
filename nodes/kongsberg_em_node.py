#!/usr/bin/env python

import rospy
import kongsberg_em.kongsberg_em
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32
import datetime
import calendar
import socket

def sonar_listener():
    rospy.init_node('kongsberg_em')
    pub = rospy.Publisher('/mbes_ping',PointCloud,queue_size=10)
    
    sonar = kongsberg_em.kongsberg_em.KongsbergEM(16112)

    while not rospy.is_shutdown():
        try:
            sonar_data = sonar.getPacket()
        except socket.error:
            break

        if sonar_data is not None:
            if sonar_data['type'] == 'xyz':
                pointCloud = PointCloud()
                pointCloud.header.frame_id = 'mbes'
                
                date_str = str(sonar_data['date'])
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                
                timestamp = datetime.datetime(year, month, day)
                timestamp += datetime.timedelta(seconds=float(sonar_data['time_of_day']))
                
                unix_timestamp = calendar.timegm(timestamp.timetuple())
                unix_timestamp += timestamp.microsecond/1000000.0
                
                pointCloud.header.stamp.from_sec(unix_timestamp)
                
                for xyz in sonar_data['beams']:
                    p = Point32()
                    #Convert from fwd, stbd, down to ROS fwd, left, up
                    p.x = xyz[0]
                    p.y = -xyz[1]
                    p.z = -xyz[2]
                    pointCloud.points.append(p)
                
                pub.publish(pointCloud)
                
if __name__ == '__main__':
    try:
        sonar_listener()
    except rospy.ROSInterruptException:
        pass
               
                
