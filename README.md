# Valheim game server on AWS

## Prerequisites

- Homebrew
- Packer & Terraform
  `brew tap hashicorp/tap`
  `brew install hashicorp/tap/packer`
  `brew install hashicorp/tap/terraform`
- Python (3.10)
  - Pip (21.3.1)

## Deployment commands

### Prebaking the AMI with Packer

Make sure you `cd` into `./packer`.

- `export AWS_ACCESS_KEY_ID="<YOUR_AWS_ACCESS_KEY_ID>"`
- `export AWS_SECRET_ACCESS_KEY="<YOUR_AWS_SECRET_ACCESS_KEY>"`
- `packer init .`
- `packer fmt .`
- `packer validate .`
- `packer build valheim-aws.pkr.hcl`

The resulting AMI will be tagged `project:vaheim`, so that it can be easily used later.

### Deploying resources using CDK

- Activate virtual environment
  - `source .venv/bin/activate`
- Install requirements
  - `pip install -r requirements.txt`
  - `pip install -r requirements-dev.txt`
- Deploy infra using CDK
  - `make bootstrap`
  - `make synth | less`
  - `make deploy`

### Uploading the initial save files to S3

- While deploying the `ValheimAwsStack`, to upload files to S3
  - make sure the S3 bucket has been provisioned before running this
  - `make upload`
- Ensure your game save files are compressed and archived into a file called `latest.tar.gz`

### Operation

- Get the `ValheimAws.ValheimFunctionUrl` from the CFN Outputs
  - pass different `action`s via the query string
  - eg `https://kq3y3633sts2v7tkbtkwajtlsm0rglbb.lambda-url.eu-west-2.on.aws/?action=status`
  - eg `https://kq3y3633sts2v7tkbtkwajtlsm0rglbb.lambda-url.eu-west-2.on.aws/?action=start`
  - eg `https://kq3y3633sts2v7tkbtkwajtlsm0rglbb.lambda-url.eu-west-2.on.aws/?action=stop`

## Destroying the resources

- Backup the files from S3
  - they will be downloaded into `./s3_files`
  - `make download`
- `make destroy`

## Lambda local invocation

- Uses [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html), so `sam` must be installed and working
- Run `make synth` first of all, such that `./cdk.out` will contain the template JSON file
- The events are available in `./lambda/events`
  - `start.json` -- sets the desired_capacity of the ASG to `1`, thus starting the game server
  - `stop.json` -- sets the desired_capacity of the ASG back to `0`
- Commands

  ```bash
  sam local invoke ValheimLambda -t ./cdk.out/ValheimAwsStack.template.json -e ./lambda/events/status.json
  sam local invoke ValheimLambda -t ./cdk.out/ValheimAwsStack.template.json -e ./lambda/events/start.json
  sam local invoke ValheimLambda -t ./cdk.out/ValheimAwsStack.template.json -e ./lambda/events/stop.json
  ```

## Misc commands

### AWS CLI commands

```bash
# SSM Run commands
su - ubuntu -c './s3_files/backup.sh'

INSTANCE_ID=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`
REGION=`wget -q -O - http://169.254.169.254/latest/meta-data/placement/region`
ASG_NAME=`aws autoscaling describe-auto-scaling-instances --region $REGION --instance-ids $INSTANCE_ID | jq -r .AutoScalingInstances[0].AutoScalingGroupName`
LIFECYCLE_NAME="TestHook"

aws autoscaling complete-lifecycle-action --lifecycle-action-result CONTINUE --region $REGION --lifecycle-hook-name $LIFECYCLE_NAME --auto-scaling-group-name $ASG_NAME --instance-id $INSTANCE_ID

# Other useful commands
aws autoscaling describe-auto-scaling-groups --filters Name=tag:project,Values=valheim | jq -r ".AutoScalingGroups[0].AutoScalingGroupName"
aws ec2 describe-instances --filters "Name=tag:project,Values=valheim" "Name=instance-state-name,Values=running" | jq -r ".Reservations[0].Instances[0].PublicIpAddress"
```

### Packer commands

- `packer init .`
- `packer fmt .`
- `packer validate .`
- `packer build valheim-aws.pkr.hcl`

### CDK commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

### venv commands

To manually create a virtualenv on MacOS and Linux:

```bash
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```bash
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
pip install -r requirements.txt
```
