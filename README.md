# Shrek AIO Flooder
Simple Python AIO Flooder for **testing** IDS and other types of systems and networks.
This tool is an All-in-one script allowing multiple options for flooding and fuzzing using **Scapy**.
The main purpose for the creation of this script is to aid in quick testing of networks and gateways.
It can be used for further retrieving metrics like volume of traffic per second, and to observe how the network or system behaves.
The usage of this tool should be done in a responsible manner and under controlled envyronments.
It is not advised for usage within enterprise and unauthorized networks. There's likely professionally-made alternatives, however, the motivation behind this creation was the lack of Python-based flooding and fuzzing tools with low requirements and dependancies, at it essentially simplifies the usage of **Scapy**, providing a _user-friendly_ CLI.

## Features
* User-friendly
* Easy to understand and modify source
* Only requires _Scapy_
* Quickly emulate different types of flooding attacks
* Requires no knowledge (_script-kid firendly_)

### Supported Flood/Fuzz:
* SYN Flood
* ACK Flood
* ACK Flood w/ previous tcp handshake
* UDP Flood w/ PPS-optimized alternative
* ~~GET & POST Floods~~
* ICMP & Ping-of-Death Floods
* ~~IKE Flood (ISAKMP)~~
* ~~6LoWPAN Flood~~
* ~~DNS   Flood (nxdomain)~~
* ~~SlowLoris~~
###### Strike-through are NYI


## Disclaimer
This tool, although public, is still a WORK IN PROGRESS project and it's development is without commitment.
Use this for educational or testing uses only. I will not be held responsible for any damages caused by the use of this tool.

