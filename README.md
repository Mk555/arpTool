# arpTool

**Script based on the python lib scapy to send arp customs arp packets. It update the iptables to redirect packets.**

## Notes

The scapy lib need root permission to run

## USAGE

`./main.py --destination <IP @> [--router <IP @>] [--iface <iface>] [--fwconf] [--freq <sec>]`

*--destination* : The IP adress of the destination of the arp packets
*--router* : The IP adress of the router (if not the same of the iface)
*--fwconfig* : Put the flag at false if you don't whant to redirect the packets send to the device you're poisoning
*--freq* : Frequency to send packets (secs)
