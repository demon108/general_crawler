#!/bin/bash
#scrapy crawl general -a seed=seed.urls -a sites=sites.dat -a single_scrapy=true > tmp.my &
#if run on server,remove '#'
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
cd /home/zzg/scrapy_general/conf/
/usr/bin/scrapy crawl general -a seed=seed.urls -a sites=sites.dat > tmp.my &
