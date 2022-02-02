#!/bin/bash
# simple script to fire up the ventilator controls and pressure monitor
# Alex Cochran 07/27/2017

echo "Starting ventilator software..."
python ~/Desktop/WIP_noulsmatic_v3/1_VentControl_v3a.py &
python ~/Desktop/WIP_noulsmatic_v3/2_vitals.py &

sleep 5s

python3 ~/Desktop/WIP_noulsmatic_v3/vitals_read_kludge.py &

wait
