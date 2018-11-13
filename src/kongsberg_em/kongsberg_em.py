#!/usr/bin/env python

import socket
import struct

class KongsbergEM:
    def __init__(self):
        self.insock = socket.socket(type=socket.SOCK_DGRAM)
        self.insock.bind(('',16112))

    def getPacket(self):
        data,addr = self.insock.recvfrom(10000)
        start,dgram_type = struct.unpack('<BB',data[:2])
        if start == 2: #start identifier
            if dgram_type == 80:
                #print 'position datagram'
                date,time = struct.unpack('<II',data[4:12])
                time = time/1000.0 # ms to s
                latitude,longitude = struct.unpack('<ii',data[16:24])
                latitude/=20000000.0
                longitude/=10000000.0
                heading, = struct.unpack('<H',data[30:32])
                heading/=100.0
                return {'type':'position', 'date':date, 'time_of_day':time, 'latitude':latitude, 'longitude':longitude, 'heading':heading}
            if dgram_type == 88:
                date,time = struct.unpack('<II',data[4:12])
                time = time/1000.0 # ms to s
                #print 'date:',date,'time of day (s):',time
                beam_count,valid_count = struct.unpack('<HH',data[24:28])
                #print 'beam count:',beam_count,'valid count:',valid_count
                beams = []
                for n in range(beam_count):
                    z,x,y,qf,detect_info = struct.unpack('<fff2xBxB',data[36+20*n:36+20*n+17])
                    if detect_info < 16:
                        beams.append((x,y,z))
                #print beams
                return {'type':'xyz', 'date':date, 'time_of_day':time, 'beams':beams}
        
if __name__ == '__main__':
    em = KongsbergEM()
    count = 0
    while count < 10:
        count += 1
        print em.getPacket()


