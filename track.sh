#!/bin/bash

while true; do
    #ps --format=%cpu,%mem,rss,vsz,cputime,comm,args -A |grep -v grep|grep pypy-env | sed -e 's/pypy.*$//'  | sed -e 's/^[ \t]*//' | sed -e 's/[ \t]*$//' | sed -e 's/[ \t][ \t]*/,/g';
    ps --format=%cpu,%mem,rss,vsz,cputime,comm,args -A |grep -v grep|grep Realign.py | sed -e 's/py.*$//'  | sed -e 's/^[ \t]*//' | sed -e 's/[ \t]*$//' | sed -e 's/[ \t][ \t]*/,/g';
    sleep 1;
done 
