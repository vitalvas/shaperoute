# -*- coding: utf-8 -*-

DB_HOST="localhost"
DB_USER="root"
DB_PASS=""
DB_NAME="shaperoute"

config={
    "arp": {
	"enable":False,
	"conf":"/usr/shaperoute/syscfg/arp.conf",
	"reload":"/usr/sbin/arp -ad > /dev/null && /usr/sbin/arp -f /usr/shaperoute/syscfg/arp.conf > /dev/null"
    },
    "dhcp": {
	"enable":False,
	"conf":"/usr/shaperoute/syscfg/dhcpd_users.conf",
	"reload":"/usr/local/etc/rc.d/isc-dhcpd restart"
    }
}



