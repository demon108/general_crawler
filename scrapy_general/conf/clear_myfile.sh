#!/bin/bash
#cd xxxx
cd /home/zzg/scrapy_general/conf
date=`date +%F`
mv scrapy.log "scrapy.log.$date"
mv req.my "req.my.$date"
mv response_get.my "response_get.my.$date"
rm *.my
rm ok_*
rm back_link*
