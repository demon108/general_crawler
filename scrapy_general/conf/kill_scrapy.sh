#!/bin/bash
ps -efw |grep scrapy |grep general|awk '{print "kill "$2}' |bash

