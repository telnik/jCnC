jCnC

This project allows system administrators to configure groups of juniper switches. 

It extends the capabilites provided by pyez in three ways.

1) It store information about devices in a local database.

2) It provides a very cron friendly command line parser

3) It is multithreaded for rapidly disseminating configuration changes.

This is alpha software.  Use at own risk.  Please send me bugs/patches!


Examples:

rcli.py --mode software --action install --device all --param /path/to/upgrade/archive

upgrade every devices software with the file found in /path/to/upgrade/archive


rcli.py -m host -a add -d 10.10.12.1 -p root,toor

add a new host to the database url 10.10.12.1, user root, password toor


rcli.py -m help

show extended help
