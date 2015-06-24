#!/bin/python

import commands
import os
import time
import datetime

def format_data(date):
    t = time.strptime(date,'%Y-%m-%d')
    return datetime.datetime(* t[:6])


clearfiles = ['scrapy','response','req']
workspace = '/home/zzg/scrapy_general/conf'
os.chdir(workspace)
status = commands.getoutput('ls')
files = status.split('\n')
now = datetime.datetime.now()
for clearfile in clearfiles:
    for f in files:
        if f.startswith(clearfile):
            scrapy_logs = f.split('.')
            if len(scrapy_logs)==3:
                filedate = format_data(scrapy_logs[2])
                diff_days = (now-filedate).days
                if diff_days>30:
                    curfile = os.path.join(workspace,f)
                    cmd = 'rm %s'%(curfile)
                    os.system(cmd)
