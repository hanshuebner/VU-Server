#!/bin/bash

. .venv/bin/activate
python3 server.py &
sleep 2
python3 loadavg-meters.py
wait
