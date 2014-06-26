#!/usr/bin/python2

import getopt, sys
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW

def usage():
	print "usage : 	-?	--help		display this message"	
	print "		-h	--host		host (name or ip) of Junos Device"
	print "		-u	--user		username to login as"
	print "		-p	--pass		password to use"
	print "		-f	--file		Juniper file to install"
	print "		-r	--reboot	time to reboot, min from now (optional)"

def InstallOnHost(hostname, username, password, softwareFilePath, rebootTime):
	dev = Device(host=hostname, user=username, password=password)
	softw = SW(dev)
	hash = SW.local_md5(softwareFilePath)

	softw.install(softwareFilePath, remote_path='/var/tmp', progress=dev, validate=False, checksum=hash, cleanfs=False, no_copy=False, timeout=1800)

	if rebootTime != 0:
		softw.reboot(rebootTime)

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
		elif opt in ("-r", "--reboot"):
			rboot = arg
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
		print "File Name of Package to Install is required"
		usage()
		sys.exit()
	else:	
		InstallOnHost(hname, uname, passw, fname, rboot)

main()
