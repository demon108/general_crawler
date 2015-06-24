import os
import sys
import time
import string
from datetime import datetime
from pymongo import MongoClient


date_pre = datetime.fromtimestamp(time.time()-3600).strftime("%Y%m%d%H")
date_str = date_pre[0:8]
hour = string.atoi(date_pre[-2:])


conn = MongoClient("192.168.241.8",27017)
links = conn.linkrelativeDB["link%s"%(date_str)]

import socket, fcntl, struct
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth1'))  
ip = socket.inet_ntoa(inet[20:24])  
s_code = string.atoi(ip.split(".")[-1])

f_list = list()
for i in range(hour+1):
	f_name = "back_link_%s%02d.dat"%(date_str,i)
	if (os.path.exists(f_name))	:
		f_list.append(f_name)

urllist= dict() 
f_len = len(f_list)
total = 0
new = 0
for j in range(f_len):
	f1 = f_list[j]
	if (os.path.exists(f1))	:
		fp = open(f1,'r')
		new = 0
		urls2 = dict() #de-dumplicate in the file(by self-parent)
		for line in fp:
			arr = line.strip().split("\t")
			if len(arr) != 3:
				continue
			url = arr[0]
			p = arr[1]
			ts = arr[2]

			key = url+p
			if urls2.has_key(key):
				continue
			else:
				urls2[key] = 1
		
			if not urllist.has_key(url):
				urllist[url] = {"url":url,"s":s_code,'d':list()}
			try:
				item = {"p":p,"ts":datetime.strptime(ts,"%Y-%m-%d %H:%M:%S.%f")}
				urllist[url]['d'].append(item) 
			except ValueError, e:
				continue
		
		fp.close()


tmp = list()	
i = 0
links.remove({"s":s_code})
links.ensure_index("url")

for d,x in urllist.items():
	tmp.append(x)
	i += 1
	if i%1000 == 0 :
		try:
			links.insert(tmp,continue_on_error=True)
			tmp = list()
		except Exception, e:
			tmp = list()
			continue

if len(tmp) > 0:
	try:
		links.insert(tmp,continue_on_error=True)
	except Exception, e:
		pass

conn.close()

if hour == 23:
	for f in f_list:
		os.unlink(f)
