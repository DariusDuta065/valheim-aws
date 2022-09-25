#!/bin/sh

sudo apt update -y
sudo apt install -y python3-pip python-setuptools awscli

sudo pip3 install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz

/usr/local/bin/cfn-init -v --region eu-west-2 --stack ValheimAwsStack --resource ValheimASG768633DF -c default
/usr/local/bin/cfn-signal -e 0 --region eu-west-2 --stack ValheimAwsStack --resource ValheimASG768633DF

# sudo /opt/aws/bin/cfn-init -v --region eu-west-2 --stack ValheimAwsStack --resource ValheimASG768633DF -c default#
# sudo /opt/aws/bin/cfn-signal -e 0 --region eu-west-2 --stack ValheimAwsStack --resource ValheimASG768633DF
