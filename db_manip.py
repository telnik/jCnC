#!/usr/bin/python2

import sys, sqlite3, argparse 

class dbmanager:
	"""
	DataStore Class for Juniper Devices
	Stores hosts, thier usernames and passwords, and groups.
	Groupes are lists of hosts with names.

	Methods:
		create_host -- insert a new host
		modify_host_name -- modify a hosts host name
		modify_host_user -- modify a hosts user name
		modify_host_pass -- modify a hosts password
		delete_host -- delete a host

		show_host -- retrieve all the info about the host
		show_all  -- retrieve all info about all hosts

		create_group -- create a new group by name
		modify_group_name -- change the name of an exsisting group
		delete_group -- delete a group
	
		show_group -- retrieve all info about all hosts in the group

		create_db -- initialize a new database

		is_host -- returns true if string matches a hostname
		is_group -- returns true if string matches a groupname
		is_member -- returns true if host is already in group
	"""

	def __init__(self):
		self.db_connection = sqlite3.connect("/var/local/pyezd/store.db", isolation_level=None)
                self.db_cursor = self.db_connection.cursor()
		
	def __exit__(self):
		self.db_connection.close()

	def create_db(self):
		self.db_cursor.execute("CREATE TABLE devices (hostname text PRIMARY KEY ON CONFLICT ABORT, username text, password text) ") 
		self.db_cursor.execute("CREATE TABLE relations (groupname text, hostname text)")
		self.db_cursor.execute("CREATE TABLE groups (groupname text PRIMARY KEY ON CONFLICT ABORT)")

	def is_host(self, host):
		self.db_cursor.execute("SELECT hostname FROM devices where hostname = ?", (host,))
		if not self.db_cursor.fetchall():
			return False
		return True

	def is_group(self, gname):
		self.db_cursor.execute("Select groupname FROM groups WHERE groupname = ?", (gname,))
                if not self.db_cursor.fetchall():
                        return False
                return True

	def is_member(self, hostname, groupname):
		self.db_cursor.execute("Select hostname FROM relations WHERE hostname = ? AND groupname = ?", (hostname, groupname))
                if not self.db_cursor.fetchall():
                        return False
                return True

	def create_host(self, host, user, passw):
		if self.is_host(host):
			return False
		self.db_cursor.execute("INSERT INTO devices VALUES (?, ?, ?)", ( host, user, passw ) )  
		return True

	def modify_host_name(self, host, newname):
		if self.is_host(newname):
			return False
		self.db_cursor.execute("UPDATE devices SET hostname = ? where hostname = ?", (host, newname) )
		return True

	def modify_host_user(self, host, newuser):
		self.db_cursor.execute("UPDATE devices SET username = ? where hostname = ?", (host, newuser) )
		return True

	def modify_host_pass(self, host, newpass):
		self.db_cursor.execute("UPDATE devices SET password = ? where hostname = ?", (host, newpass) )
		return True

	def delete_host(self, host):
		self.db_cursor.execute("DELETE FROM devices where hostname = ?", (host,) )
		self.db_cursor.execute("DELETE FROM relations where hostname = ?", (host,) )
		return True

	def show_host(self, host):
		self.db_cursor.execute("SELECT * FROM devices WHERE hostname = ?", (host,) )
		return self.db_cursor.fetchall()

	def show_all(self):
		self.db_cursor.execute("SELECT * FROM devices")
		return self.db_cursor.fetchall()

	def create_group(self, gname):
		if self.is_host(gname):
			return False
		if self.is_group(gname):
			return False
		self.db_cursor.execute("INSERT INTO groups VALUES (?)", (gname,))
		return True

	def delete_group(self, gname):
		self.db_cursor.execute("DELETE FROM groups WHERE groupname = ?", (gname,))
		self.db_cursor.execute("DELETE FROM relations WHERE groupname = ?", (gname,))

	def modify_gname(self, oldname, newname):
		if self.is_group(newname):
                        return False
		if self.is_group(newname):
                        return False
		self.db_cursor.execute("UPDATE groups SET groupname = ? where groupname = ?", (newname, oldname))
		return True

	def show_group(self, gname):
		self.db_cursor.execute("SELECT devices.hostname, devices.username, devices.password FROM devices, relations, groups WHERE devices.hostname = relations.hostname AND relations.groupname = groups.groupname AND groups.groupname = ?", (gname,))
		return self.db_cursor.fetchall()

	def attach(self, hostname, groupname):
		if self.is_member(hostname, groupname):
			return False
		self.db_cursor.execute("INSERT INTO relations VALUES (?, ?)", (groupname, hostname))
		return True

	def detach(self, hostname, groupname):
		self.db_cursor.execute("DELETE FROM relations WHERE hostname = ? AND groupname = ?", (hostname, groupname))


