import requests
from time import sleep
import argparse
import json
import sys

# cli arguments
parser = argparse.ArgumentParser(description="Search breachdirectory", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-e", dest="email", required=False, help="someone@somewhere.com")
parser.add_argument("-o", dest="output", required=False, type=argparse.FileType("w", encoding="UTF-8"), help="Output csv file", default="breach-out.json")
parser.add_argument("-l", dest="elist", required=False, type=argparse.FileType("r", encoding="UTF-8"), help="Email list")

args = parser.parse_args()
semail = args.email
outfile = args.output
emlist = args.elist

if len(sys.argv)==1:
	parser.print_help(sys.stderr)
	sys.exit(1)

headers = {
	"X-RapidAPI-Key": "",
	"X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"
}

def esingle(single):
	url = "https://breachdirectory.p.rapidapi.com/"
	querystring = {"func":"auto","term":single}
	response = requests.get(url, headers=headers, params=querystring)
	print(response.text)
	if response.status_code == 200:
		with open(outfile.name, mode='a') as out:
			out.write(single+'\n'+response.text+'\n')
def emult():
	with open(emlist.name, mode='r') as em:
		for user in em:
			user2 = user.strip()
			esingle(user2)

if __name__ == "__main__":
	if semail:
		esingle(semail)
	elif emlist:
		emult()
