#!/bin/bash
 if [ "$#" -eq  "0" ]
   then
     echo "No arguments supplied"
     echo "Usage: ./asn_v4.sh <ASN> "
     exit
else
curl --silent https://www.dan.me.uk/bgplookup?asn=$1 |grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\/[0-9]\{1,2\}' |sort |uniq
fi
