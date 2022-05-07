#!/usr/bin/python3
# API info get

import sys
import re
import argparse
import requests
import signal
import urllib3
import os
import json
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait, FIRST_COMPLETED

parser = argparse.ArgumentParser(description="API info grabber", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-t", dest="target", required=True, help="Api Target, ex: http(s)://target.com", default="")
parser.add_argument("-a", dest="apilist", required=True, type=argparse.FileType("r", encoding="UTF-8"), help="Api list")
parser.add_argument("-b", dest="prox", required=False, help="Proxy through burp", action="store_true")
parser.add_argument("-o", dest="savefile", required=True, type=argparse.FileType("w", encoding="UTF-8"), help="Output file")

args = parser.parse_args()
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

target = args.target
apilit = args.apilist
apilist = [line.rstrip('\n') for line in apilit]
savefil = args.savefile
savefile = savefil.name
prox = args.prox
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def handler(signum, frame):
    res = input(" Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
signal.signal(signal.SIGINT, handler)
if prox == True:
    proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080' }
else:
    proxies = ""
print("[*] api info grabber")
s = requests.session()
def doit(API):
    try:
        api2 = API.strip()
        target2 = target+api2
        def getreq():
            r = s.get(target2, verify=False, timeout=40, allow_redirects=False, proxies=proxies)
            print("[-] Response from "+target2+" "+str(r.status_code))           
            if r.status_code == 200:
                apiout = open(savefile, "a+")
                apiout.write(target2+"\n")
                pretty_json = json.loads(r.text)
                apiout.write(json.dumps(pretty_json, indent=2)+"\n\n")
                apiout.close()
        getreq()
    except requests.exceptions.ProxyError:
        print("[!] Cannot connect to proxy")        
    except requests.exceptions.Timeout:
        print("[!] Response from "+target2+" Response Timeout")
        pass
    except requests.exceptions.ConnectionError:
        print("Connection error")
        pass
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects")
        pass
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
# Start the load operations and mark each future with its host
    future_to_api = {executor.submit(doit, API): API for API in apilist}
            