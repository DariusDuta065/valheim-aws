#!/bin/sh

# SSM Run commands
su - ubuntu -c './s3_files/backup.sh'

INSTANCE_ID=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`

REGION=`wget -q -O - http://169.254.169.254/latest/meta-data/placement/region`

ASG_NAME=`aws autoscaling describe-auto-scaling-instances --region $REGION --instance-ids $INSTANCE_ID | jq -r .AutoScalingInstances[0].AutoScalingGroupName`

LIFECYCLE_NAME="TestHook"

aws autoscaling complete-lifecycle-action --lifecycle-action-result CONTINUE --region $REGION --lifecycle-hook-name $LIFECYCLE_NAME --auto-scaling-group-name $ASG_NAME --instance-id $INSTANCE_ID

# aws autoscaling describe-auto-scaling-groups --filters Name=tag:project,Values=valheim | jq -r ".AutoScalingGroups[0].AutoScalingGroupName"
# aws ec2 describe-instances --filters "Name=tag:project,Values=valheim" "Name=instance-state-name,Values=running" | jq -r ".Reservations[0].Instances[0].PublicIpAddress"
