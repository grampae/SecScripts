########################################
#List of targets activerecon.sh path/to/sub/file directory
########################################
slack_channel="#recon"

  
  printf "\nStarting ActiveRecon\n\n"
  printf "Sublist: $1\n"
  printf "Working Directory: $2\n" 
  mkdir -p ~/recon/$2 > /dev/null
  mkdir -p ~/recon/$2/$target > /dev/null
  mv ~/recon/$2/nmapout.xml ~/recon/$2/nmapout-old.xml > /dev/null
  mv ~/recon/$2/httpports.txt ~/recon/$2/httpports-old.txt > /dev/null
  mv ~/recon/$2/nmapreport.html ~/recon/$2/nmapreport-old.html > /dev/null
  mv ~/recon/$2/ffuf.txt ~/recon/$2/ffuf-old.txt > /dev/null
  printf "Starting Nmap\n"
  nmap -T4 -R -iL $1 -Pn -oX ~/recon/$2/nmapout.xml
  ~/tools/nmap-parse-output/nmap-parse-output ~/recon/$2/nmapout.xml http-ports > ~/recon/$2/httpports.txt
  ~/tools/nmap-parse-output/nmap-parse-output ~/recon/$2/nmapout.xml html-bootstrap > ~/recon/$2/nmapreport.html

  printf "Starting FFUF\n"
  ~/tools/ffuf -c -w ~/recon/$2/httpports.txt:HFUZZ -w ~/tools/dicc.txt:WFUZZ -t 100 -u HFUZZ/WFUZZ -mode clusterbomb -mc 200,204 -v -of html -o ~/recon/$2/ffuf.html

  zip -r -q ~/recon/$2/arecon.zip ~/recon/$2/
  curl -F file=@~/recon/$2/arecon.zip -F initial_comment=$2/activerecon -F channels=$slack_channel -H "Authorization: Bearer " https://slack.com/api/files.upload > /dev/null

printf "\n\nDone!\n"
