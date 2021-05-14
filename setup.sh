#!/usr/bin/env bash

echo "[#] installing apt packages"
sudo apt install python3-pip

echo
echo "[#] installing python modules"
sudo pip3 install -r requirements.txt

echo
echo "[#] creating systemd service"

echo "generating service file"
echo "[Unit]
Description=lichtkrant systemd service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$PWD
ExecStart=/bin/bash $PWD/run.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target" >> lichtkrant.service

echo "installing service"
sudo mv lichtkrant.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable lichtkrant

echo "starting service"
sudo systemctl restart lichtkrant

echo
echo "[#] finished installation"


