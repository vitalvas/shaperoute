#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web, ConfigParser

config = ConfigParser.RawConfigParser()
config.read('settings.ini')

urls = ('.*', 'ParkPage')

class ParkPage:
	def page(self):
		web.header('Refresh', config.get('parking', 'refresh'))
		web.header('Cache-Control', 'no-cache')
		web.header('Pragma', 'no-cache')
		web.header('Content-Type', 'text/html; charset=utf-8')
		return """<html>
		<head><title>STOP</title></head>
		<body style='text-align:center;'><h1>Access denied</h1></body>
		</html>
		"""
	def POST(self):
		return self.page()
	def GET(self):
		return self.page()

app = web.application(urls, locals())

if __name__ == "__main__":
	app.run()
else:
	wsgi_app = app.wsgifunc()
