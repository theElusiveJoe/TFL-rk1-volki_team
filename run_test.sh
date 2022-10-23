#!/bin/bash

rm -f total_points.txt monsters pass.txt
for (( count=1; count<=87; count++ ))
  do
    echo Test "$count"
    ./test_gen
    timeout 30 python3.7 ./main.py
    ./test_check_log
    rm -f test.CFG
    ./test_count
    rm -f result 
  done
./total_count
rm -f witness.txt
read -s -n 1