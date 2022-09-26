# Valheim game server on AWS

## CDK commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

## Deployment commands

- Activate virtual environment
  - `source .venv/bin/activate`
- Install requirements
  - `pip install -r requirements.txt`
  - `pip install -r requirements-dev.txt`
- Deploy infra using CDK
  - `make bootstrap`
  - `make synth | less`
  - `make deploy`
- While deploying the `ValheimAwsStack`, to upload files to S3
  - make sure the S3 bucket has been provisioned before running this
  - `make upload`

## Lambda local invocation

- Uses [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html), so `sam` must be installed and working
- Run `make synth` first of all, such that `./cdk.out` will contain the template JSON file
- The events are available in `./lambda/events`
  - `start.json` -- sets the desired_capacity of the ASG to `1`, thus starting the game server
  - `stop.json` -- sets the desired_capacity of the ASG back to `0`
- Commands

  ```bash
  sam local invoke ValheimLambda -t ./cdk.out/ValheimAwsStack.template.json -e ./lambda/events/start.json
  sam local invoke ValheimLambda -t ./cdk.out/ValheimAwsStack.template.json -e ./lambda/events/stop.json
  ```

## venv commands

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
