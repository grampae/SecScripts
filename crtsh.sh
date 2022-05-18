#!/bin/bash
 echo "Enumerating subdomains from crt.sh hostname: $1";echo
 curl -s "https://crt.sh/?q=$1"| html2text | awk '{print $5}'| sort|uniq
 echo  
