#!/bin/bash

echo "Welcome to the PyEz demo"
echo ""
echo "This program demonstrates the functionality of the "
echo "Juniper python control software with four simple examples"
echo ""
echo "Example 1:"
echo "Getting all the hardware summaries of the devices"
echo ""
echo "This demonstrates the speed at which data can be gathered from the cluster"
time ./rcli.py -m cli -a terminal -p "show chassis hardware" -d all
echo ""
echo "The biggest bottleneck is setting up the connections, but because everything runs in parallel it is possible to querry every device on the network in less than 40 seconds"
echo ""
echo "Example 2:"
echo "This next example shows how you can use the software to retrieve information and reconfigure other devices"
echo ""
echo "The progam is retrieving a complete list of the vlans on the network, it will then sort them, and display them as a list of commands"
echo ""
echo "These commands can be stored as a file, and then run against other hosts that need to know about vlans"
./rcli.py -m cli -a terminal -p "show configuration vlans | display set"  -d all | grep "set vlans" | sort | uniq 
echo ""
echo "Example 3"
echo "This example searches all the devices for interfaces that have physical communication problems"
echo ""
echo "If any are found the interface will be printed to the screen, this takes a little longer so be please be patient"
./rcli.py -m cli -a terminal -p "show interfaces media detail | match \"physical|crc\"" -d all | grep -v "0                0\|Down\|master\|root" | grep -B 1 "CRC\|reply"
echo ""
echo "Example 4:"
echo "This final demonstration shows how the software can be used to ensure SLAs are met"
echo ""
echo "The devices will be querried for their uptimes, and then a number will be given to show the average network uptime for the devices querried"
echo ""
./rcli.py -m cli -a terminal -p "show system uptime" -d all | grep up | grep days | cut -d u -f 2 | cut -d " " -f 2 | paste -sd+ - | awk '{print "("$0}'  | awk '{print $0")/14"}' - | bc |  awk '{print $0" days average uptime"}'
echo ""
echo "Similar things can be done to show network loads and statistically demonstrate trends"
echo ""
echo "Any Questions?"
read ch


