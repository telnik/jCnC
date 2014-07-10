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

import sys, threading, argparse, paramiko
from Queue import Queue
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from db_manip import dbmanager

def cliparser_help():
	return "\n\
        kvargs \n\
                mode = [ configure | software | cli | info | host | group | help ]\n\
                host = [ <host-id> | <group-id> | all ] \n\
                action = [ < depends on mode, see below > ]\n\
                param = [ < depends on mode, see below > ]\n\
        \n\
        mode descriptions and options\n\
                configure:      manipuate juniper configuration on <host> - actions:\n\
                                commit - commit changes\n\
                                        param - timeout-minutes, if ommited, default value\n\
                                commit_check - perform the commit check operation \n\
                                        param - rollback number 0-50\n\
                                load - load changes into the candidate config\n\
                                save - save the configuration to the local host\n\
                                        param is path to save file\n\
                                lock - take an exclusive lock on the candidate config\n\
                                unlock - release the exclusive lock\n\
                                rollback - perform the load rollback command\n\
                                        param - rollback number 0-50\n\
                software:       perform software updates \n\
                                install - perform entire software install\n\
                                        param - location of file to install on local host\n\
                                rollback - same as 'request softare rollback'\n\
                cli:    run juniper cli commands on <host> - actions:\n\
                                terminal        param is cli command in quotes\n\
                                file    param is path to file with juniper commands\n\
                host:   manipulate host database - actions:\n\
                                add     param - user,password\n\
                                modify_id\n\
                                modify_pass\n\
                                modify_user\n\
                                        param for modify_* is the new value\n\
                                delete\n\
                                show\n\
                \n\
                group:  manipulate groups  \n\
                                create\n\
                                delete\n\
                     		show_groups\n\
				show_members\n\
                                join    param - group-id\n\
                                leave   param - group-id\n\
                info:   get info about <host> - actions:\n\
                                active-ports\n\
                                hardware\n\
                                alarms\n\
                                ...etc... more to come\n\
                help:           Show menu options\n\
\n\
        host descriptions and options\n\
                <host-id>:      apply actions to this host id found in the database\n\
                <group-id>:     apply actions to the hosts found in this group\n\
                all:            apply actions to all hosts in the database\n\
\n"

class jCommand(threading.Thread):
	def __init__(self, **kvargs):
		self.mode = kvargs.get('mode', False)
		self.action = kvargs.get('action', False)
		self.param = kvargs.get('param', False)
		self.host = kvargs.get('host', False)
		self.user = kvargs.get('user', False)
		self.passw = kvargs.get('passw', False)
		self.result = kvargs.get('host') + " reply:\n"
		threading.Thread.__init__(self)

	def get_result(self):
		return self.result

	def start_shell(self):
		shell = paramiko.SSHClient()
		shell.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		shell.connect(self.host, username=self.user, password=self.passw)
		return shell

	def run(self):
		# import pdb; pdb.set_trace() # dbg
		dev = Device(host=self.host, user=self.user, password=self.passw)
		try:
			dev.open(auto_probe=7)
		except:
			self.result += "Could not connect to host\n"
			return

		if not self.mode:
			self.result += "A mode of operation must be specified"
		elif self.mode == "configure":
			confc = Config(dev)
			if self.action == "commit":
				self.result += confc.commit(confirm=True, comment="Commited " + str( datetime.datetime.now() ) + " by jCnC")
			elif self.action == "commit_check":
				if confc.commit_check():
					self.result += "Commit Check Succeeds"
				else:
					self.result += "Commit Check Failed"
			elif self.action == "diff":
				x = int(self.param)
				self.result += confc.diff() #self.param)
			elif self.action == "load":
				self.result += confc.load(path=param, overwrite=True, format='conf')
			elif self.action == "lock":
				self.result += confc.lock()
			elif self.action == "rescue":
				self.result += confc.rescue(param)
			elif self.action == "rollback":
				self.result += confc.rollback(param)
			elif self.action == "save":
				self.result += "Not implemented yet" 
			elif self.action == "unlock":
				self.result += confc.unlock()
			else:
				self.result += "Configuration Action not found"
		elif self.mode == "software":
			softw = SW(dev)
			if self.action == "install":
				hash = str('')
				with open(param+'.md5') as hashfile:
					hash = hashfile.read()
				hashfile.closed()
				self.action += softw.install(param, remote_path='/var/tmp', progress=dev, validate=False, checksum=hash, cleanfs=False, no_copy=False, timout=1800) 
			elif action == "rollback":
				self.action += softw.rollback()
		elif self.mode == "cli":
			shell = self.start_shell()
			if self.action == "terminal":
				stdin, stdout, stderr = shell.exec_command("cli")
				stdin.write(self.param + '\n')
				stdin.write("exit\n")
				stdin.flush()
				for line in stdout.readlines():
					self.result += line 
			elif self.action == "file":
				self.result += "\n"
				stdin, stdout, stderr = shell.exec_command("cli")
				cfile = open(self.param, 'r')
				for line in cfile:
					stdin.write(line + '\n')
				stdin.write("exit\n")
				data = stdout.readlines()
				for line in data:
					self.result += "\n" + line
			shell.close()
		elif self.mode == "info":
			shell = self.start_shell()
			if self.action == "alarms":
				stdin, stdout, stderr = shell.exec_command("cli show chassis alarms")
				data = stdout.readlines()
				for line in data:
					self.result += line
			elif self.action == "active_ports":
				stdin, stdout, stderr = shell.exec_command('cli show interfaces terse | grep -v  "\.0" | grep -v down')
				data = stdout.readlines()
				for line in data:
					self.result += line
			elif self.action == "inactive_ports":
				stdin, stdout, stderr = shell.exec_command('cli show interfaces terse | grep -v  "\.0" | grep down')
				data = stdout.readlines()
				for line in data:
					self.result += line
			else:
				self.result += "Information Action not found"
			shell.close()
		else:
			self.result = "Operation Mode not found"

		dev.close()
		self.result += "\n"

	
def run_commands(hosts, mode, action, param):
	def prod(q, hosts):
		for host in hosts:
			thread = jCommand(host=host[0], user=host[1], passw=host[2], mode=mode, action=action, param=param)
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
	result = str('')
	for line in finished:
		result += '\n' + line
	return result

def cliparser(**kvargs):
	mode = kvargs.get('mode', False)
	host = kvargs.get('host', False)
	action = kvargs.get('action', False)
	param = kvargs.get('param', False)

	mode = str(mode)
	host = str(host)
	action = str(action)
	param = str(param)

	ishost = False
	jdb = dbmanager()
	# find and initilize device objects if not a create or an add
	if mode != "group" and action != "create" and action != "add":
		if host == "all":
			host = jdb.show_all()
			ishost = "all"
		else:
			if jdb.is_host(host):
				host = jdb.show_host(host)
				ishost = "host"
			elif jdb.is_group(host):
				host = jdb.show_group_members(host)
				ishost = "group"
			else:
				return "Hostname not found in database"

	if not mode:
		return "A mode of operation must be specified"
	elif mode == "configure" or mode == "software" or mode == "cli" or mode == "info":
		if mode == "software" and action == "install":
			hashpath = param + '.md5'
			hashfile = open(hashpath, 'w')
			hashfile(SW.local_md5(param))
		return run_commands(host, mode, action, param)
	elif mode == "host":
		if action == "add":
			paramS = param.split(",")
			if jdb.create_host(host, paramS[0], paramS[1]):
				return "Host Successfully Created"
			else:
				return "Host Creation Failed"
		elif action == "modify_id":
			result = str('')
			for hostid in host:
				if jdb.modify_host_name(hostid[0], param):
					result += "\n" + hostid[0] + " Host Successfully Modified"
				else:
					result += "\n" + hostid[0] + " Host Modification Failed"
			return result
		elif action == "modify_pass":
			if jdb.modify_host_pass(host[0][0], param):
				return "Password Successfully Modified"
		elif action == "modify_user":
			result = str('')
			for hostid in host:
				if jdb.modify_host_user(hostid[0], param):
					result += "\n" + hostid[0] + " User Successfully Modified"
				else:
					result += "\n" + hostid[0] + " User Modification Failed"
			return result
		elif action == "delete":
			result = str('')
			for hostid in host:
				if jdb.delete_host(hostid[0], param):
					result += "\n" + hostid[0] + " Deleted"
				else:
					result += "\n" + "Could not delete " + hostid[0] 
		elif action == "show":
			result = str('')
			for hostid in host:
				result += "\nHostname : " + str(hostid[0])
				result += "\nUsername : " + str(hostid[1])
				result += "\nPassword : " + str(hostid[2])
				result += "\n"
			return result
		else:
			return "Host Action not found"
	elif mode == "group":
		if action == "join":
			if jdb.is_member(host, param) or jdb.is_member(param, host):
				return "Already a member"
			elif jdb.is_group(host) and jdb.is_host(param):
				return jdb.attach(host, param)
			elif jdb.is_group(param) and jdb.is_host(host):
				return jdb.attach(param, host)
			return "A vaild group and host must be provided"
		elif action == "leave":
			if jdb.is_member(host, param) or jdb.is_member(param, host):
				if jdb.is_group(host) and jdb.is_host(param):
					return jdb.detach(host, param)
				if jdb.is_group(param) and jdb.is_host(host):
					return jdb.detach(param, host)
				return "A vaild group and host must be provided"
			else:
				return "Host not a member"
		elif action == "delete":
			return jdb.delete_group(host)
		elif action == "show_group_members":
			if jdb.is_group(host) == False:
				return host + " is not a group"
			result = str('')
			for hostid in host:
				result += "\n" + hostid[0]
			return result
		elif action == "create":
			return jdb.create_group(host)
		elif action == "show_groups":
				host = jdb.show_group_members(host)
                                result = "Groups:"
                                groups = jdb.show_group_names()
                                for group in groups:
                                        result += "\n" + group[0]
                                return result
		else:
			return "Action not understood"
	elif mode == "help":
		return cliparser_help()
	else:
		return "Mode " + mode + " not found"

parser = argparse.ArgumentParser(description='Parallel Juniper Command Execution', epilog="For more detailed help use --mode help")
parser.add_argument('-m', '--mode', nargs=1, help="Mode of operation", required=True)
parser.add_argument('-d', '--device', nargs=1, help="Device/Group/All to operate on")
parser.add_argument('-a', '--action', nargs=1, help="Action inside the mode of operation")
parser.add_argument('-p', '--param', nargs=1, help="Additional information required by action")

args = parser.parse_args()
host = args.device
action = args.action
param = args.param

if host == None:
	host = False
else:
	host = host[0]
if action == None:
	action = False
else:
	action = action[0]
if param == None:
	param = False
else:
	param = param[0]

print cliparser(mode=args.mode[0], host=host, action=action, param=param)


