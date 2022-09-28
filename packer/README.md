# Valheim AWS Packer

Packer is used to configure an AMI that has LinuxGSM, SteamCMD and all the other dependencies installed.
The only thing that's left to do whenever a new instance boots is to download the latest game save files and start the server.
This reduced the deployment time from 7 minutes to around 1.5 minutes. 😊

## Commands to build an AMI

- `export AWS_ACCESS_KEY_ID="<YOUR_AWS_ACCESS_KEY_ID>"`
- `export AWS_SECRET_ACCESS_KEY="<YOUR_AWS_SECRET_ACCESS_KEY>"`
- `packer init .`
- `packer fmt .`
- `packer validate .`
- `packer build valheim-aws.pkr.hcl`

The resulting AMI will be tagged `project:vaheim`, so that it can be easily used later.
