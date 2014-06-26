#!/usr/bin/python2
import sys
from jnpr.junos import Device
from jnpr.junos.utils.start_shell import StartShell
from db_manip import dbmanager

def cliparser_help():
	print("
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
                                diff - return the diff string between running and candidate config                                   
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
                                        ie "set interfaces xe-0/0/1 family inet unit 0 adress 192.168.1.1"                   
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
")

def cliparser(**kvargs):
	mode = kvargs.get('mode', False)
	host = kvargs.get('host', False)
	action = kvargs.get('action', False)
	param = kvargs.get('param', False)


	# find and initilize device objects
	if host == "all":
		host = dbmanager.show_all()
	else:
		if dbmanager.is_host(host):
			host = dbmanager.show_host(host)
		elif dbmanager.is_group(host):
			host = dbmanager.show_group(host)

	if not mode:
		return "A mode of operation must be specified"
	elif mode == "configure": 
		if action == "commit":

		elif action == "commit_check":

		elif action == "diff":

		elif action == "load":

		elif action == "lock":

		elif action == "rescue":

		elif aciton == "rollback":

		elif action == "unlock":

		else:
			return "Configuration Action not found"
	elif mode == "software"
	elif mode == "cli"
	elif mode == "info"
	elif mode == "host"
		jdb = dbmanager()
		if action = "add":
			hostar = param.split(",")
			if jdb.create_host(hostar[0], hostar[1], hostar[2]):
				return "Host Successfully Created"
			else:
				return "Host Creation Failed"
		elif action = "modify_id":
			if jdb.modify_host_name(host, param):
				return "Host Successfully Modified"
			else:
				return "Host Modification Failed"
		elif action = "modify_pass":
			if jdb.modify_host_pass(host, param):
				return "Host Successfully Modified"
		elif action = "modify_user":
			jdb.modify_host_user(host, param)
		elif action = "delete":
			jdb.delete_host(host, param)
		elif action = "show":
			return jdb.show(host)
		else:
			return "Host Action not found"
	elif mode == "group"
	elif mode == "help"
		return cliparser_help()


