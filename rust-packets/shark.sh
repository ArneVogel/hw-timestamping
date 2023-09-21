#!/bin/sh
sudo tshark -f "port not 53 and not arp and not tcp and not stp and not icmp6" -i enp65s0f0np0 "$@"
