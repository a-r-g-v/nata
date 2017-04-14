#!/bin/sh -e

sudo mv /tmp/app.systemd /etc/systemd/system/app.service
sudo mkdir -p /app
sudo mv /tmp/app.py /app/app.py

sudo apt-get install -y && sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip python3-dev -y
sudo pip3 install Flask==0.11

sudo systemctl enable app
sudo systemctl start app

