#!/usr/bin/env -S ../bin/python

from mido import Message
from mido.sockets import PortServer, connect
from time import sleep

# swap the ip for the correct one
output = connect('127.0.0.1', 8100)

def genpacket(status, note, velocity):
    return Message(status, note=note, velocity=velocity)

while True:
    try:
        raw_ = input("length note velocity:\nmidi> ").split()

        timeout, note, velocity = int(raw_[0]), int(raw_[1]), int(raw_[2])
        
        msg_on = genpacket("note_on", note, velocity)

        print("<{}".format(msg_on))
        output.send(msg_on)

        msg_off = genpacket("note_off", note, 0)
        sleep(timeout)
        output.send(msg_off)

        #output.send(Message('note_on', note=60, velocity=70))
        #output.send(Message('note_off', note=60))

    except KeyboardInterrupt:
        break
