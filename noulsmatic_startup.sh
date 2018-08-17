#!/bin/bash
# simple script to fire up the ventilator controls and pressure monitor
# Alex Cochran 07/27/2017

echo "Starting ventilator software..."
python ~/Desktop/noulsmatic_v2/1_VentControl_v2a.py &
python ~/Desktop/noulsmatic_v2/2_vitals.py &

wait
