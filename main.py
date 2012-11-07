#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, hashlib, re, logging
import web
import datetime, time

from settings import *
from regxp import *

#web.config.debug=False

urls = (
	'/', 'index',
	'/login', 'LoginPage',
	'/stats', 'StatusPage',
	'/users', 'UsersPage',
	'/favicon.ico', 'Icon',
	'/activateuser', 'ActivatePage',
	'/adduser', 'AddUserPage',
	'/channels', 'ChannelsPage',
	'/grps', 'GroupsPage',
	'/edituser', 'EditUserPage',
	'/removeuser', 'RemoveUserPage',
	'/syscmd/reinit', 'SysReinitPage',
	'/syscmd/reboot', 'SysRebootPage',
	'/syscmd/halt', 'SysHaltPage'
)


render = web.template.render('templates')
app = web.application(urls, locals())

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('ses_tmp'), {'loggedin': False, 'username': '', 'acl': '', 'realname': ''})
    web.config._session = session
else:
    session = web.config._session

db = web.database(dbn='mysql', db=DB_NAME, user=DB_USER, pw=DB_PASS, host=DB_HOST)

os.system("/usr/bin/touch ses_tmp/tmp")
os.system("/bin/rm ses_tmp/*")

def pipe(num, speed):
    num = int(num)
    speed = int(speed)
    if speed<1024:
        os.system("/sbin/ipfw pipe %(num)s config bw %(speed)sKbit/s" % locals())
    else:
	speed = speed/1024
	os.system("/sbin/ipfw pipe %(num)s config bw %(speed)sMbit/s" % locals())

def ipfw_flush():
    os.system("/sbin/ipfw -q -f pipe flush")
    os.system("/sbin/ipfw -q -f queue flush")

def ipfw_tbs_flush():
    os.system("/sbin/ipfw -q table 12 flush")
    os.system("/sbin/ipfw -q table 13 flush")
#    os.system("/sbin/ipfw -q table 2 flush")
#    os.system("/sbin/ipfw -q table 3 flush")


def config_pipes():
    pipes=pipe_start
    db.query("TRUNCATE TABLE pipes")
    users = db.select('users', what='id,ip,bw_up,bw_down', vars=locals())
    for u in users:
	id=u.id
	ip=u.ip
	bwup=u.bw_up
	bwdown=u.bw_down
	pipe(pipes,bwup)
	pipes_out=pipes
	pipes=pipes+1
	pipe(pipes,bwdown)
	pipes_in=pipes
	pipes=pipes+1
	db.insert('pipes', user=int(id), pipe_in=int(pipes_in), pipe_out=int(pipes_out))


def config_speed():
    perm_users = db.select('users', what='id,ip', where='active=true')
    for u in perm_users:
	ip = u.ip
	ids = u.id
	ids = int(ids)
	speeds = db.select('pipes', what='pipe_in,pipe_out', where="user='$ids'", vars=locals())[0]
	speed_in = speeds.pipe_in
	speed_out = speeds.pipe_out
	os.system("/sbin/ipfw -q table 12 add %(ip)s %(speed_out)d"  % locals()) # upload
	os.system("/sbin/ipfw -q table 13 add %(ip)s %(speed_in)d" % locals()) # download


def config_tables():
    channels = db.select('channels', where='active=true', vars=locals())
    for cn in channels:
	ids=int(cn.id)
	table=(cn.table)
	if ids and table:
	    os.system("/sbin/ipfw -q table %(table)s flush" % locals())
	    users = db.select('users', what='ip', where="channel='$ids'", vars=locals())
	    for usr in users:
		ip=usr.ip
		if ip:
		    os.system("/sbin/ipfw -q table %(table)s add %(ip)s" % locals())


def config_reject_sites():
    sites = db.select('sites', where='status=true', vars=locals())
    for s in sites:
	network=s.network
	os.system("/sbin/ipfw -q table 2 add %(network)s" % locals())


def config_users_sites():
    users = db.select('users', where='limit_sites=true', vars=locals())
    for usr in users:
	ip=usr.ip
	os.system("/sbin/ipfw -q table 3 add %(ip)s" % locals())


def config_static_arp():
    users = db.select('users', what='ip,mac', where="mac!='' and mac!='00:00:00:00:00:00'", vars=locals())
    conf = open(arp_conf, "wt")
    for user in users:
	ip = user.ip
	mac = user.mac
	print >> conf, "%(ip)s %(mac)s" % locals()
    conf.close()
    os.system("arp -ad" % locals())
    os.system("arp -f %(arp_conf)s" % globals())


def config_dhcp():
    users = db.select('users', what='id,ip,mac', where="mac!='' and mac!='00:00:00:00:00:00'", vars=locals())
    config = []
    conf = open(dhcp_conf, "wt")
    for user in users:
	ip = user.ip
	mac = user.mac
	username = user.id
	print >> conf, "host %(username)s { fixed-address %(ip)s; hardware ethernet %(mac)s; }" % locals()
    conf.close()
    os.system(dhcp_reset)

def reconfig():
    print 'Flushing ipfw pipes and queues'
    ipfw_flush()
    print 'Configure pipes'
    config_pipes()
    print 'Fludhing ipfw tables'
    ipfw_tbs_flush()
    print 'Configure ipfw pipes'
    config_speed()
    print 'Configure ipfw tables'
    config_tables()
#    print 'Configure ipfw reject networks'
#    config_reject_sites()
#    print 'Configure ipfw users to reject networks'
#    config_users_sites()
#    print 'Configure dhcp'
#    config_dhcp()
#    print 'Configure static arp'
#    config_static_arp()
    print 'Started'


reconfig()


web.config.session_parameters['cookie_name'] = 'ssid'
web.config.session_parameters['cookie_domain'] = None
web.config.session_parameters['timeout'] = 60*60
web.config.session_parameters['ignore_expiry'] = False
web.config.session_parameters['ignore_change_ip'] = False
web.config.session_parameters['secret_key'] = '$1Aiq35(B*$23D73&%'
web.config.session_parameters['expired_message'] = render.exp_session()


class Icon:
    def GET(self):
	web.redirect('/static/icons/user.png')

class LoginPage:
    def GET(self):
	if web.input().get('out', '0') == '1':
	    session.kill()
	if not session.loggedin:
	    return render.main(u'Logging in', render.login(), session)
	else:
	    web.redirect('/')
    def POST(self):
	if not session.loggedin:
	    username = web.input().get('username')
	    passwds = hashlib.md5(web.input().get('password')).hexdigest()
	    qq = db.select('admins', what="COUNT(id) AS num", where="login=$username AND passwd=$passwds AND active=true", vars=locals())
	    for u in qq:
		cnt = u.num
	    if cnt==1:
		try:
		    session.loggedin=True
		    session.username=username
		    dbs = db.select('admins', what='acl_full,realname', where='login=$username', limit='1', vars=locals())
		    for w in dbs:
			session.acl = w.acl_full
			session.realname = w.realname
		finally:
		    web.redirect('/')
	    else:
		web.redirect('/')
	else:
	    web.redirect('/')


class ActivatePage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    userid = int(web.input().get("id"))
	    act = int(web.input().get("act"))
	    try:
		if userid != 0:
		    if act == 1:
			db.update('users', where='id=$userid', active='true', vars=locals())
			ips = db.select('users', what='ip', where='id=$userid', limit='1', vars=locals())[0]
			ip = ips.ip
			sps = db.select('pipes', what='COUNT(id) AS num', where='user=$userid', limit='1', vars=locals())[0]
			cnt = sps.num
			if cnt == 1:
			    sp = db.select('pipes', what='pipe_in,pipe_out', where='user=$userid', limit='1', vars=locals())[0]
			    sp_in = sp.pipe_in
			    sp_out = sp.pipe_out
			    os.system("/sbin/ipfw -q table 12 add %(ip)s %(sp_out)d" % locals())
			    os.system("/sbin/ipfw -q table 13 add %(ip)s %(sp_in)d" % locals())
			else:
			    reconfig()
		    if act == 2:
			db.update('users', where='id=$userid', active='false', vars=locals())
			ips = db.select('users', what='ip', where='id=$userid', limit='1', vars=locals())[0]
			ip = ips.ip
			os.system("/sbin/ipfw -q table 12 delete %(ip)s" % locals())
			os.system("/sbin/ipfw -q table 13 delete %(ip)s" % locals())
		else:
		    if act == 77:
			qq = db.query("UPDATE users SET active='false'")
			os.system("/sbin/ipfw -q table 12 flush")
			os.system("/sbin/ipfw -q table 13 flush")
		    if act == 88:
			qq = db.query("UPDATE users SET active='true'")
			ips = db.select('users', what='id,ip')
			for c in ips:
			    ip = c.ip
			    ids = c.ip
			    sps = db.select('pipes', what='COUNT(id) AS num', where='user=$ids', limit='1', vars=locals())[0]
			    cnt = sps.num
			    if cnt == 1:
				sp = db.select('pipes', what='pipe_in,pipe_out', where='user=$ids', limit='1', vars=locals())[0]
				sp_in = sp.pipe_in
				sp_out = sp.pipe_out
				os.system("/sbin/ipfw -q table 12 add %(ip)s %(sp_out)d" % locals())
				os.system("/sbin/ipfw -q table 13 add %(ip)s %(sp_out)d" % locals())
			    else:
				reconfig()
	    finally:
		web.redirect("/users")


class ChannelsPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    channels = db.select('channels', vars=locals())
	    return render.main(u'Channels list', render.channellist(channels), session)

class GroupsPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    grps = db.select('users_grp', vars=locals())
	    return render.main(u'Groups list', render.grplist(grps), session)



class AddUserPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    return self.show(web.input(), False)

    def POST(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    user = web.input()
	    try:
		if not ipaddrp(user.ipaddr):
		    raise ValueError
		user_ip = user.get('ipaddr')
		user_mac = user.get('hwaddr')
		if hwaddrp(user_mac) is False:
		    user_mac = '00:00:00:00:00:00'
		qq = db.select('users', what='COUNT(id) AS num', where='ip=$user_ip', vars=locals() )[0]
		if qq.num !=0:
		    raise ValueError;
		else:
		    db.insert('users',
				realname=user.get('realname', ''),
				groups=int(user.get('grps', '')),
				ip=user_ip,
				mac=user_mac,
				channel=int(user.get('channel', '')),
				bw_up=int(user.get('bw_up', '')),
				bw_down=int(user.get('bw_down', ''))
			    )
		    config_dhcp()
		    config_static_arp()
		    web.redirect('/users')
	    except ValueError:
		return self.show(user, True)

    def show(self, input, error):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    channels = db.select('channels', what="id,name", where="active=true", vars=locals())
	    grps = db.select('users_grp', what="id,name", where="active=true", vars=locals())
	    return render.main(u'Add user', render.adduser(input, error, channels, grps),session)


class index:
    def GET(self):
	if not session.loggedin:
	    web.redirect('/stats')
	else:
	    web.redirect("/users")

class StatusPage:
    def GET(self):
	ipaddr = web.webapi.ctx['ip']
	user = list(db.select('users', where='ip=$ipaddr', vars=locals()))
	if len(user) < 1:
	    web.redirect('/login')
	    return
	user = user[0]
	return render.main(u'Status page', '', session)

class UsersPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    if web.input().get('grp'):
		ids = int(web.input().get('grp'))
		if ids:
		    users = db.select('users_full', where='groups=$ids', vars=locals())
		else:
		    users = db.select('users_full')
	    else:
		users = db.select('users_full')
	    groups = db.select('users_grp')
	    cnt = db.select('users', what='COUNT(id) AS num', vars=locals())[0]
	    cnt = cnt.num
	    cnt1 = db.select('users', what='COUNT(id) AS num', where="active='false'", vars=locals())[0]
	    cnt1 = cnt1.num
	    if cnt == cnt1:
		trn = 22
	    if cnt != cnt1:
		trn = 33
	    dt = datetime.datetime.now()
	    hash = time.mktime(dt.timetuple())
	    return render.main('Users list', render.usertable(users,groups,trn,hash,cnt), session)

class EditUserPage:
    def show(self, input, error):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    channels = db.select('channels', what='id,name', where="active=true", vars=locals())
	    grps = db.select('users_grp', what='id,name', where="active=true", vars=locals())
	    count_channels = db.query("SELECT COUNT(*) AS total FROM channels")[0]
	    count_channels = count_channels.total
	    userid = int(web.input().get("id"))
	    return render.main('Edit user', render.edituser(input, error, channels, grps, count_channels), session)

    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    userid = int(web.input().get("id"))
	    user = db.select('users', where='id=$userid', vars=locals())[0]
	    return self.show(user, False)

    def POST(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    user = web.input()
	    try:
		mac_addr = user.mac
		if hwaddrp(mac_addr) is False:
		    mac_addr = '00:00:00:00:00:00'
		if not ipaddrp(user.get('ip','')):
		    raise ValueError
		db.update('users', where='id=$user.id', 
			    realname=user.realname,
			    groups=int(user.grps),
			    ip=user.ip,
			    mac=user.mac,
			    limit_sites=user.limitsites,
			    channel=int(user.channel),
			    bw_up=int(user.bw_up),
			    bw_down=int(user.bw_down),
			    vars=locals()
			)
		config_dhcp()
		web.redirect("/")
	    except ValueError:
		return self.show(user, True)

class SysReinitPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    try:
		reconfig()
	    finally:
		return render.main('Done', '', session)

class SysRebootPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    if session.acl == "true":
		os.system('/sbin/shutdown -r now')
		return render.main('Rebooted server', '', session)
	    else:
		return render.main('Sorry. You do not have permission. :(', '', session)

class SysHaltPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    if session.acl == "true":
		os.system('/sbin/shutdown -p now')
		return render.main('Halted server', '', session)
	    else:
		return render.main('Sorry. You do not have permission. :(', '', session)




class RemoveUserPage:
    def GET(self):
	if not session.loggedin:
	    web.redirect("/login?out=1")
	else:
	    userid = int(web.input().get("id"))
	    if userid:
		try:
		    user = db.select('users', what='ip', where='id=$userid', vars=locals())[0]
		    ip = user.ip
		    db.delete('users', where="id=$userid", vars=locals())
		    db.delete('pipes', where='user=$userid', vars=locals())
		    os.system("/sbin/ipfw -q table 12 delete %(ip)s" % locals())
		    os.system("/sbin/ipfw -q table 13 delete %(ip)s" % locals())
#		    reconfig()
		finally:
		    web.redirect('/')



if __name__ == "__main__":
    app.run()
