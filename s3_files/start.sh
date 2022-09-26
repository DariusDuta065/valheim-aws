#!/bin/bash

# Install the game server
wget -O linuxgsm.sh https://linuxgsm.sh
chmod +x linuxgsm.sh
bash linuxgsm.sh vhserver

./vhserver auto-install

# Restore latest backup
cd ~/s3_files/
tar -xf latest.tar.gz

cd backup/
mv vhserver.cfg ~/lgsm/config-lgsm/vhserver/

mkdir -p ~/.config/unity3d/IronGate/Valheim/
mv Valheim/ ~/.config/unity3d/IronGate/

# Start the game server
cd ~
./vhserver start
