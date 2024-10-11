#!/bin/bash
#find subdomains and http servers from a file containing root domain names
#usage: findsub.sh domain.list subdmainoutput.txt httpoutput.csv
#Define the locations of your all.txt and resolvers.txt files below
#requires replacing paths with your own and these tools
#amass: https://github.com/OWASP/Amass
#massdns: https://github.com/blechschmidt/massdns
#subfinder: https://github.com/projectdiscovery/subfinder
#puredns: https://github.com/d3mondev/puredns
#gotator: https://github.com/Josue87/gotator
#dnsx: https://github.com/projectdiscovery/dnsx
#httpx: https://github.com/projectdiscovery/httpx
#all.txt: https://gist.github.com/jhaddix/f64c97d0863a78454e44c2f7119c2a6a
domain=$1
p=$1echo
subout=$2
httpout=$3
w=working.out
s=sorted.out
if [ -f $domain ]; then
	start_time="$(date -u +%s)"
	echo "Finding subdomains with amass"
	/home/grampae/Tools/amass enum --active --brute -df $domain  -o amass.out
	echo "Finding subdomains with subfinder"
	subfinder -dL $domain -o subfinder.out
	echo "Finding subdomains with puredns"
	for i in $(cat ${domain}); do
		puredns bruteforce /someplace/Wordlists/all.txt $i -r /someplace/massdns/lists/resolvers.txt >>puredns.out
	done
	cat amass.out > $w
	cat subfinder.out >> $w
	cat puredns.out >> $w
	sort -u $w > $s
	rm $w
	echo "Starting gotator for permutations"
	gotator -sub $s >>$w
	echo "Resolving hosts with dnsx"
	dnsx -l $w -o tmp -r /someplace/massdns/lists/resolvers.txt
	cat tmp >tmp2
	cat $s >>tmp2
	sort -u tmp2 > $subout
	rm $w $s amass.out subfinder.out puredns.out tmp tmp2
	#httpx ingests data from subdomain findings and checks top http ports
	echo "Finding http servers with httpx"
	httpx -l $subout -sc -ct -location -title -server -td -ip -http2 -vhost -cname -asn -cdn -csv -rt -lc -wc -pipeline -p 66,80-83,88,443,445,457,888,1080,1100,1241,1352,1433,1434,1521,1944,2301,3000,3128,3306,4000-4002,4100,4443,5000,5432,5800-5802,6346,6347,7001,7002,8000,8001,8009,8080-8083,8181,8443,8880,8888,9000,9001,9080,9090,9999,10000,30821 -o $httpout
	end_time="$(date -u +%s)"
	elapsed="$(($end_time-$start_time))"
	echo "Total of $elapsed seconds elapsed to process list"
else
	echo "Supplied domain file does not exist or is not usable"
fi
