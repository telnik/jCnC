#!/usr/bin/python2

import getopt, sys, datetime
from jnpr.junos import Device
from jnpr.junos.utils.config import Config 

def usage():
	print "usage : 	-?	--help		display this message"	
	print "		-h	--host		host (name or ip) of Junos Device"
	print "		-u	--user		username to login as"
	print "		-p	--pass		password to use"
	print "		-f	--file		Juniper config file to load"

def ConfigHost(hostname, username, password, filepath):
	dev = Device(host=hostname, user=username, password=password)
	confd = Config(dev)
	confd.load(path=filepath, overwrite=True, format='conf')
	if confd.commit_check():
		print "Configuration Succeeded, Commiting Now."
		confd.commit(confirm=True, comment="Commited " + str( datetime.datetime.now() ) + " by pyezd")
	else:
		print "Configuration Check Failed, changes discarded"

	dev.close()

def main():
	hname=0 
	uname=0 
	passw=0 
	fname=0 
	rboot=0
		
	try:
		opts, args = getopt.getopt(sys.argv[1:], "?h:u:p:f:", ["help", "host=", "user=", "pass=", "file="])
	except getopt.GetoptError as err:
		print str(err)	
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-?", "--help"):
			usage()
			sys.exit()
		elif opt in ("-h", "--host"):
			hname = arg
		elif opt in ("-u", "--user"):
			uname = arg
		elif opt in ("-p", "--pass"):
			passw = arg
		elif opt in ("-f", "--file"):
			fname = arg
		else:
			assert False, "unhandled option"
	if hname == 0:
		print "Hostname is required"
		usage()
                sys.exit()
	elif uname == 0:
		print "Username is required"
		usage()
		sys.exit()
	elif passw == 0:
		print "Password is required"
		usage()
		sys.exit()
	elif fname == 0:
		print "File Name of Configuration File is required"
		usage()
		sys.exit()
	else:	
		ConfigHost(hname, uname, passw, fname)
main()
