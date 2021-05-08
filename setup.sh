#!/usr/bin/env bash

echo '[#] installing apt packages'
sudo apt install python3-pip 

echo
echo '[#] installing python modules'
sudo pip3 install -r requirements.txt

echo
echo '[#] creating systemd service'

echo 'generating service file'
echo '[Unit]' > lichtkrant.service
echo 'Description=lichtkrant systemd service' >> lichtkrant.service
echo '' >> lichtkrant.service
echo '[Service]' >> lichtkrant.service
echo 'Type=simple' >> lichtkrant.service
echo "WorkingDirectory=$PWD" >> lichtkrant.service
echo "ExecStart=/bin/bash $PWD/run.sh" >> lichtkrant.service
echo 'Restart=always' >> lichtkrant.service
echo 'User=root' >> lichtkrant.service
echo '' >> lichtkrant.service
echo '[Install]' >> lichtkrant.service
echo 'WantedBy=multi-user.target' >> lichtkrant.service

echo 'installing service'
sudo mv lichtkrant.service /etc/systemd/system
sudo systemctl daemon-reload

echo
echo '[#] finished installation'


