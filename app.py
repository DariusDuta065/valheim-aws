#!/usr/bin/env python3
import os
import aws_cdk as cdk

from valheim_aws.valheim_aws_stack import ValheimAwsStack

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

valheim_stack = ValheimAwsStack(app, "ValheimAws", env=env)
cdk.Tags.of(valheim_stack).add("project", "valheim")

app.synth()
