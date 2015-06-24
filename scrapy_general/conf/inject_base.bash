#/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
cd /home/zzg/scrapy_general/conf/
#cd /home/zzg/coopinion/focus_crawler/you/conf
/usr/bin/python ../tools/inject_seeds.py base.dat
