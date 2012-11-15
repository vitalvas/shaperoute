#!/bin/sh
#
# PROVIDE: shaperoute
# REQUIRE: DAEMON mysql
# KEYWORD: shutdown

. /etc/rc.subr

name="shaperoute"
rcvar=`set_rcvar`

load_rc_config $name

: ${shaperoute_enable="NO"}

pidfile="/var/run/${name}.pid"

case "$1" in
start)
    if [ -f /usr/shaperoute/main.py ]; then
	echo "Starting shaperoute"
	cd /usr/shaperoute
	/usr/local/bin/python /usr/shaperoute/main.py 127.0.0.1:9002 > /var/log/shaperoute.log 2>&1 &
	pgrep -f python /usr/shaperoute/main.py > ${pidfile}
    fi
    ;;
stop)
    if [ -f ${pidfile} ]; then
	echo "Stopping shaperoute"
	kill `cat ${pidfile}`
	`rm ${pidfile}`
    else
	echo "Stopping shaperoute"
	kill `pgrep -f python /usr/shaperoute/main.py`
    fi
    ;;
*)
    echo "Usage: `basename $0` {start|stop}" >&2
    exit 64
    ;;
esac
exit 0
