#!/bin/bash
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -A FORWARD -o wlan0 -i brvirt -s 10.3.1.0/24 -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A POSTROUTING -t nat -j MASQUERADE

