#!/usr/bin/python3
#send messages or files over pushover, can also pipe commands via 'somecommand | ./push.py'
#replace device name, user and token key after 'default=' or supply your own via commandline
import requests
import argparse
import sys

parser = argparse.ArgumentParser(description="Pushover Client", formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-f", dest="pfile", required=False, type=argparse.FileType("r", encoding="UTF-8"), help="File to send")
parser.add_argument("-m", dest="message", required=False, help="Message", default="Here is a file")
parser.add_argument("-d", dest="device", required=False, help="Device name", default="replaceme")
parser.add_argument("-u", dest="userkey", required=False, help="User key", default="replaceme")
parser.add_argument("-t", dest="token", required=False, help="Token key", default="replaceme")
parser.add_argument('stdin', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

args = parser.parse_args()

if len(sys.argv)==1 and sys.stdin.isatty():
    parser.print_help(sys.stderr)
    sys.exit(1)
    
device = args.device
userkey = args.userkey
ptoken = args.token


if not sys.stdin.isatty():
    msg = parser.parse_args().stdin.read()
else:
    stdin = []
    msg = args.message

if args.pfile:
	pfile = args.pfile.name
	files = { "attachment": (pfile, open(pfile, "rb"), "image/jpeg") }
else:
	files = ""
data = { "token": ptoken, "user": userkey, "message": msg , "device": device}
try:
	r = requests.post("https://api.pushover.net/1/messages.json", data = data, files = files)
except Exception as e:
	print(e)
