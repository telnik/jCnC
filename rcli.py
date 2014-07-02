#!/usr/bin/python2

"""
Copyright (c) 2014 Timothy Elniski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys, threading, argparse
from Queue import Queue
from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from db_manip import dbmanager

def cliparser_help():
	print("""
        kvargs 
                mode = [ configure | software | cli | info | host | group | help ]
                host = [ <host-id> | <group-id> | all ] 
                action = [ < depends on mode, see below > ]
                param = [ < depends on mode, see below > ]
        
        mode descriptions and options
                configure:      manipuate juniper configuration on <host> - actions:
                                commit - commit changes
                                        param - timeout-minutes, if ommited, default value
                                commit_check - perform the commit check operation 
                                        param - rollback number 0-50
                                load - load changes into the candidate config
                                save - save the configuration to the local host
                                        param is path to save file
                                lock - take an exclusive lock on the candidate config
                                unlock - release the exclusive lock
                                rollback - perform the load rollback command
                                        param - rollback number 0-50
                software:       perform software updates 
                                install - perform entire software install
                                        param - location of file to install on local host
                                rollback - same as 'request softare rollback'
                cli:    run juniper cli commands on <host> - actions:
                                terminal        param is cli command in quotes
                                file    param is path to file with juniper commands
                host:   manipulate host database - actions:
                                add     param - user,,,password
                                modify_id
                                modify_pass
                                modify_user
                                        param for modify_* is the new value
                                delete
                                show
                
                group:  manipulate groups  
                        if host is group - actions:
                                create
                                add     param - host-id
                                remove  param - host-id
                                delete
                                show
                        if host is host - actions:
                                join    param - group-id
                                leave   param - group-id
                info:   get info about <host> - actions:
                                active-ports
                                hardware
                                alarms
                                ...etc... more to come
                help:           Show menu options

        host descriptions and options
                <host-id>:      apply actions to this host id found in the database
                <group-id>:     apply actions to the hosts found in this group
                all:            apply actions to all hosts in the database
""")

class jCommand(threading.Thread):
	def __init__(self, **kvargs):
		self.mode = kvargs.get('mode', False)
		self.action = kvargs.get('action', False)
		self.param = kvargs.get('param', False)
		self.host = kvargs.get('host', False)
		self.user = kvargs.get('user', False)
		self.passw = kvargs.get('pass', False)
		self.result = kvargs.get('host') + " reply: "
		threading.Thread.__init__(self)

	def get_result(self):
		return self.result

	def run(self):
		try:
			dev = Device(host=host, user=user, password=passw)
			dev.open()

			if not mode:
				self.result += "A mode of operation must be specified"
			elif mode == "configure":
				confc = Config(dev)
				if action == "commit":
					self.result += confc.commit(confirm=True, comment="Commited " + str( datetime.datetime.now() ) + " by jCnC")
				elif action == "commit_check":
					self.result += confc.commit_check()
				elif action == "diff":
					self.result += confc.diff(param)
				elif action == "load":
					self.result += confc.load(path=param, overwrite=True, format='conf')
				elif action == "lock":
					self.result += confc.lock()
				elif action == "rescue":
					self.result += confc.rescue(param)
				elif action == "rollback":
					self.result += confc.rollback(param)
				elif action == "save":
					self.result += "Not implemented yet" 
				elif action == "unlock":
					self.result += confc.unlock()
				else:
					self.result += "Configuration Action not found"
			elif mode == "software":
				softw = SW(dev)
				if action == "install":
					with open(param+'.md5') as hashfile:
						hash = hashfile.read()
					hashfile.closed()
					self.action += softw.install(param, remote_path='/var/tmp', progress=dev, validate=False, checksum=hash, cleanfs=False, no_copy=False, timout=1800) 
				elif action == "rollback":
					self.action += softw.rollback()
			elif mode == "cli":
				shell = StartShell(dev)
				shell.open()
				if action == "terminal":
					self.result += shell.run(param)
				elif action == "file":
					self.result += "\n"
					cfile = open(param, 'r')
					for line in cfile:
						self.result += shell.run(line)
				shell.close()

			elif mode == "info":
				shell = StartShell(dev)
				shell.open()
				if action == "alarms":
					self.result += shell.run("show chassis alarms")
				elif action == "active_ports":
					self.result += shell.run('show interfaces terse | except "\.0" | except down')
				else:
					self.result += "Information Action not found"
			else:
				self.result = "Operation Mode not found"
		except:
			self.result += " encountered an exception: " + sys.exc_info()[0] 
			
	
def run_commands(hosts, mode, action, param):
	def prod(q, hosts):
		for host in hosts:
			thread = jCommand(host=host[0], user=host[1], passw=[2], mode=mode, action=action, param=param)
			thread.start()
			q.put(thread, True)

	finished = []
	def cons(q, total_hosts):
		while len(finished) < total_hosts:
			thread = q.get(True)
			thread.join()
			finished.append(thread.get_result())
	q = Queue(5)
	prod_thread = threading.Thread(target=prod, args=(q, hosts))
	cons_thread = threading.Thread(target=cons, args=(q, len(hosts)))
	prod_thread.start()
	cons_thread.start()
	prod_thread.join()
	cons_thread.join()

def cliparser(**kvargs):
	mode = kvargs.get('mode', False)
	host = kvargs.get('host', False)
	action = kvargs.get('action', False)
	param = kvargs.get('param', False)

	ishost = False
	jdb = dbmanager()
	# find and initilize device objects
	if host == "all":
		host = jdb.show_all()
		ishost = "all"
	else:
		if jdb.is_host(host):
			host = jdb.show_host(host)
			ishost = "host"
		elif jdb.is_group(host):
			host = jdb.show_group(host)
			ishost = "group"

	if not mode:
		return "A mode of operation must be specified"
	elif mode == "configure" or mode == "software" or mode == "cli" or mode == "info":
		if mode == "software" and action == "install":
			hashpath = param + '.md5'
			hashfile = open(hashpath, 'w')
			hashfile(SW.local_md5(param))
		run_commands(host, mode, action, param)
	elif mode == "host":
		if action == "add":
			paramS = param.split(",")
			if jdb.create_host(host, paramS[0], paramS[1]):
				return "Host Successfully Created"
			else:
				return "Host Creation Failed"
		elif action == "modify_id":
			if jdb.modify_host_name(host, param):
				return "Host Successfully Modified"
			else:
				return "Host Modification Failed"
		elif action == "modify_pass":
			if jdb.modify_host_pass(host, param):
				return "Host Successfully Modified"
		elif action == "modify_user":
			jdb.modify_host_user(host, param)
		elif action == "delete":
			jdb.delete_host(host, param)
		elif action == "show":
			return jdb.show_host(host)
		else:
			return "Host Action not found"
	elif mode == "group":
		if ishost == "host":
			if action == "join":
				return jdb.attach(param, host)
			elif action == "leave":
				return jdb.detach(param, host)
			else:
				return "Action not understood"
		elif ishost == "group":
			if action == "add":
				return jdb.attach(host, param)
			elif action == "remove":
				return jdb.detach(host, param)
			elif action == "delete":
				return jdb.delete_group(host)
			elif action == "show":
				return jdb.show_group(host)
			else:
				return "Action not understood"
		else:
			if action == "create":
				return jdb.create_group(host)
			else:
				return "Group not understood"
	elif mode == "help":
		return cliparser_help()

parser = argparse.ArgumentParser(description='Parallel Juniper Command Execution', epilog="This program runs like an AK-47 with the safty off, be careful what you tell it to do.  It's very easy to destroy all your switches")
parser.add_argument('-m', '--mode', nargs=1, help="Mode of operation", required=True)
parser.add_argument('-d', '--device', nargs=1, help="Device/Group/All to operate on")
parser.add_argument('-a', '--action', nargs=1, help="Action inside the mode of operation")
parser.add_argument('-p', '--param', nargs=1, help="Additional information required by action")

args = parser.parse_args()

print cliparser(mode=args.mode, host=args.device, action=args.action, param=args.param)
