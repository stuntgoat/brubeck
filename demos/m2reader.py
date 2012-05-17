#!/usr/bin/env python

import zmq

ctx = zmq.Context()
s = ctx.socket(zmq.SUB)
s.connect("tcp://127.0.0.1:9955")
s.setsockopt(zmq.SUBSCRIBE, "")

while True:
    msg = s.recv()
    print msg
