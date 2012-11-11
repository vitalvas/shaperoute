# -*- coding: utf-8 -*-

config={
    "database": {
	"host":"localhost",
	"user":"root",
	"passwd":"",
	"name":"shaperoute"
    },
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



