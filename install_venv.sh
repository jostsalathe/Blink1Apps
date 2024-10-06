#!/bin/bash

sudo apt install -y python3-venv
python3 -m venv ./myvenv
./myvenv/bin/pip install blink1
./myvenv/bin/pip install psutil

