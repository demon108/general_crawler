#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
#cd /home/zzg/coopinion/focus_crawler/you/conf
#cd /disk1/you_scrapy/conf
/usr/local/bin/python ../tools/import_back_link.py &
