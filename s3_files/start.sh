#!/bin/bash

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
