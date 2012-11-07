# -*- coding: utf-8 -*-

import re, sys


ip_regex  	= r"^(?:\d{1,3}\.){3}\d{1,3}$"
mac_regex 	= r"^(?:[0-9a-fA-F]{2}\:){5}[0-9a-fA-F]{2}$"
username_regex	= r"^[a-zA-Z0-9\_]{1,}$"


def escape(s):
    return s.replace("'", "''")

def ipaddrp(s):
#    s=s.strip()
    if re.match(ip_regex, s):
	return True
    else:
	return False

def hwaddrp(s):
#    s=s.strip()
    if re.match(mac_regex, s):
	return True
    else:
	if s == '' or s == ' ':
	    return True
	else:
	    return False

def usernamep(s):
#    s=s.strip()
    if re.match(username_regex, s):
	return True
    else:
	return False


