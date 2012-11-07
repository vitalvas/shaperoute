#!/bin/csh

arp -an | grep 'expires' | sed 's/(//' | sed 's/)//' | awk '{print "UPDATE users SET mac=\"" $4 "\" WHERE ip=\"" $2 "\" and mac=\"00:00:00:00:00:00\";"}' | mysql shaperoute

