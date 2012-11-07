#!/bin/sh

cd /usr/shaperoute
/usr/local/bin/python /usr/shaperoute/main.py 127.0.0.1:9002 > /var/log/shape.log 2>&1 &
sleep 2
if [ -f /var/run/shape.pid ]
then
    rm /var/run/shape.pid
fi
ps -ax | grep 'python main.py' | grep -v '8900' | awk '{print $1}' > /var/run/shape.pid



