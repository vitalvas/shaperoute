#!/bin/sh

cd /usr/shaperoute
/usr/local/bin/python /usr/shaperoute/main.py 127.0.0.1:9002 > /var/log/shape.log 2>&1 &
