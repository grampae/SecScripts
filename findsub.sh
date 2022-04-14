#!/bin/bash
domain=$1
out=$2
w=working.out
s=sorted.out
amass enum --active --brute -d $domain -o amass.out
subfinder -d $domain -o subfinder.out
puredns bruteforce /media/grampae/extradrive1/Wordlists/all.txt $domain -r /home/grampae/Tools/massdns/lists/resolvers.txt >puredns.out
cat amass.out > $w
cat subfinder.out >> $w
cat puredns.out >> $w
sort -u $w > $s
rm $w
gotator -sub $s > $w
dnsx -l $w -o tmp
cat tmp >tmp2
cat $s >>tmp2
sort -u tmp2 > $out
rm $w $s amass.out subfinder.out puredns.out tmp tmp2
echo done
