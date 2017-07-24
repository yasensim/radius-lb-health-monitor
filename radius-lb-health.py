#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2015 VMware, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# Author Yasen Simeonov, simeonovy at vmware com
__author__ = 'yasensim'

import radius, logging, daemon
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

### Edit below this line according to your enviropment ###
RAD_SECRET = "testing123"
RAD_USER = "nsx-lb-test"
RAD_PASS = "VMware1!"
HTTP_PORT = 8081
### Do not Edit below this line!!! ###

class httpHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
	LOG.info("Healthcheck from "+str(self.client_address))
        self._set_headers()
        self.wfile.write(self.__checkRAD())

    def do_HEAD(self):
        self._set_headers()

    def __checkRAD(self):
	r = radius.Radius(RAD_SECRET, host='127.0.0.1', port=1812)
	try:
	    if r.authenticate(RAD_USER, RAD_PASS):
		LOG.info("Authentication successful!")
		return 'Success'
	    else:
		LOG.error("RADIUS is UP but cannot authenticate!!!")
		return 'Failure'
	except radius.SocketError as e:
	    LOG.error("Cannot connect to RADIUS: "+ str(e) )
	return 'Failure'

def run_hc():
    global LOG
    LOG = logging.getLogger("nsx-lb-healthcheck")
    LOG.setLevel(logging.INFO)
    handler = logging.FileHandler('/var/log/nsx-lb-healthcheck.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    LOG.addHandler(handler)
    server_class = HTTPServer
    httpd = server_class(('0.0.0.0', HTTP_PORT), httpHandler)
    try:
	httpd.serve_forever()
    except KeyboardInterrupt:
	pass
    httpd.server_close()
def main():
    with daemon.DaemonContext():
	run_hc()

if __name__ == '__main__':
    main()
