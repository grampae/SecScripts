

#!/bin/bash########################################
#Single target: recon.sh target domain
#List of targets recon.sh path/to/file
########################################
slack_token=""
slack_channel="#recon"
if [ $# == 2 ]
then
  touch ~/argtemp.txt
  printf "$1 $2\n" > ~/argtemp.txt
  cat ~/argtemp.txt
else
  cat "$1" > ~/argtemp.txt
fi

while read target domain
  do
  printf "\nStarting Recon1\n\n"
  printf "Target: $target\n"
  printf "Domain: $domain\n"  
  mkdir -p ~/recon/$target
  mkdir -p ~/recon/$target/$domain
  touch ~/recon/$target/$domain/subdomains.txt
  touch ~/recon/$target/$domain/aquatone_urls-old.txt
  touch ~/recon/$target/$domain/aquatone_urls.txt
  mv ~/recon/$target/$domain/aquatone_urls.txt ~/recon/$target/$domain/aquatone_urls-old.txt  

  printf "\nRunning Subfinder\n"
  subfinder -silent -d $domain >> ~/recon/$target/$domain/subdomains.txt

  printf "\nRunning Amass\n"
  timeout 10m amass enum --brute --active -r 1.1.1.1,1.0.0.1,8.8.8.8,8.8.4.4,9.9.9.9,9.9.9.10,77.88.8.8,77.88.8.1,208.67.222.222,208.67.220.220 -exclude IPToASN,ShadowServer,NetworksDB,TeamCymru,HackerTarget,Robtex,RADb -nf ~/recon/$target/$domain/subdomains.txt -d $domain >> ~/recon/$target/$domain/subdomains.txt

  printf "\nSearching Project Sonar\n"
  curl http://dns.bufferover.run/dns?q=.$domain | jq .FDNS_A | cut -d ',' -f 2 | cut -d '"' -f 1 | sed '1d;$d' >> ~/recon/$target/$domain/subdomains.txt  
  sort -u ~/recon/$target/$domain/subdomains.txt > ~/recon/$target/$domain/subdomains-nodupes.txt
  mv ~/recon/$target/$domain/subdomains-nodupes.txt ~/recon/$target/$domain/subdomains.txt  

  printf "\nRunning Takeover\n"
  takeover -l ~/recon/$target/$domain/subdomains.txt -o ~/recon/$target/$domain/takeover.txt
  
  printf "\nRunning Aquatone port scan and screenshotting\n"
  cat ~/recon/$target/$domain/subdomains.txt | timeout 60m aquatone --chrome-path ~/Tools/chrome-linux/chrome -resolution 800,600 -out ~/recon/$target/$domain -ports xlarge

#  ~/tools/ffuf -c -w ~/recon/$target/$domain/aquatone_urls.txt:HFUZZ -w ~/tools/dicc.txt:WFUZZ -t 100 -u HFUZZWFUZZ -mode clusterbomb -mc 200,204 -v -of html -o ~/recon/$target/$domain/ffuf.html

  sort -u ~/recon/$target/$domain/aquatone_urls.txt > ~/recon/$target/$domain/aquatone_urls-nodupes.txt
  mv ~/recon/$target/$domain/aquatone_urls-nodupes.txt ~/recon/$target/$domain/aquatone_urls.txt
  zip -r -q ~/recon/$target/$domain/aquatone.zip ~/recon/$target/$domain/
  printf "\nSending Results to Slack\n"
  curl -F file=@~/recon/$target/$domain/aquatone.zip -F initial_comment=$target/$domain/zipped_report -F channels=$slack_channel -H "Authorization: Bearer $slack_token" https://slack.com/api/files.upload > /dev/null
  curl -F file=@~/recon/$target/$domain/aquatone_urls.txt -F initial_comment=$target/$domain/urls -F channels=$slack_channel -H "Authorization: Bearer $slack_token" https://slack.com/api/files.upload > /dev/null
  curl -s -F file=@~/recon/$target/$domain/aquatone_urls-onlynew.txt -F initial_comment=$target/$domain/new-urls -F channels=$slack_channel -H "Authorization: Bearer $slack_token" https://slack.com/api/files.upload > /dev/null
  curl -F file=@~/recon/$target/$domain/takeover.txt -F initial_comment=$target/$domain/subdomaintakeover -F channels=$slack_channel -H "Authorization: Bearer $slack_token" https://slack.com/api/files.upload > /dev/null
done <~/argtemp.txt
rm ~/argtemp.txt
printf "\n\nDone!\n"
