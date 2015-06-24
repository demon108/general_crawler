#!/bin/bash
cd /home/zzg/scrapy_general/conf/
date=`date +%F`
mv scrapy.log "scrapy.log.$date"
ps -efw |grep scrapy |grep general|awk '{print "kill -9 "$2}' |bash

