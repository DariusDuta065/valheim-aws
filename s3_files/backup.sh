#!/bin/bash

# Important files:
# - vhserver.cfg --- ~/lgsm/config-lgsm/vhserver/vhserver.cfg
# - the whole `/Valheim` directory --- ~/.config/unity3d/IronGate/Valheim

mkdir -p ~/backup
cp ~/lgsm/config-lgsm/vhserver/vhserver.cfg ~/backup/
cp -r ~/.config/unity3d/IronGate/Valheim/ ~/backup/

CURR_DATE=`date +%Y-%m-%d`
FILE_NAME="$CURR_DATE.tar.gz"

tar -zcvf $FILE_NAME ./backup/*
aws s3 cp $FILE_NAME s3://valheim-aws/$FILE_NAME
aws s3 cp $FILE_NAME s3://valheim-aws/latest.tar.gz

rm -r backup $FILE_NAME