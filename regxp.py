# -*- coding: utf-8 -*-

import re, sys


ip_regex  	= r"^(?:\d{1,3}\.){3}\d{1,3}$"
mac_regex 	= r"^(?:[0-9a-fA-F]{2}\:){5}[0-9a-fA-F]{2}$"

def ipaddrp(s):
    if re.match(ip_regex, s):
	return True
    else:
	return False

def hwaddrp(s):
    if re.match(mac_regex, s):
	return True
    else:
	return False



