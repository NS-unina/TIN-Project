#!/bin/sh


echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
sudo apt-get update

sudo apt install python3
sudo apt -y install python3-flask


