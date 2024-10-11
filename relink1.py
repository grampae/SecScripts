#!/usr/bin/python3
#Manage rebrandly short links, used during engagement where subdomain takeover happened.
import requests
import json
import argparse
import sys
import signal
import pandas as pd

# cli arguments
parser = argparse.ArgumentParser(description="Rebrandly short url creation", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-o", dest="original", required=False, help="https:/something.somewhere.com")
parser.add_argument("-l", dest="list", required=False, help="List current shortlinks", action="store_true")

args = parser.parse_args()
orig = args.original
linklist = args.list
api = 'INSERT API KEY HERE'

requestHeaders = {
  "Content-type": "application/json",
  "apikey": api,
}

if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)

def handler(signum, frame):
    res = input(" Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
signal.signal(signal.SIGINT, handler)

def dmns():
	r = requests.get('https://api.rebrandly.com/v1/domains?orderBy=createdAt&orderDir=desc&limit=100&active=true&type=user', headers=requestHeaders)
	rj = json.loads(r.text)
	print("Domains available:")
	li = [item.get('fullName') for item in rj]
	for x in li:
		print (x)
	domain = input("Which domain name would you like to use: ")
	dostuff(domain)
	
def dostuff(domain):
	
	linkRequest = {
	  "destination": orig
	  , "domain": { "fullName": domain }
	}

	r = requests.post("https://api.rebrandly.com/v1/links", 
	    data = json.dumps(linkRequest),
	    headers=requestHeaders)

	if (r.status_code == requests.codes.ok):
	    link = r.json()
	    print("Long URL was %s, short URL is %s" % (link["destination"], link["shortUrl"]))

def lst():
	r = requests.get('https://api.rebrandly.com/v1/links?orderBy=createdAt&orderDir=desc&limit=100&favourite=false&status=active', headers=requestHeaders)
	print("Available links:")
	df = pd.read_json(r.text)
	print(df[['title','shortUrl','destination','clicks']])
	
if __name__ == "__main__":
	if orig:
		dmns()
	elif linklist:
		lst()
