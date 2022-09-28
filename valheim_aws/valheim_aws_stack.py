import json
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,

    aws_s3 as _s3,
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_events as _eventbridge,
    aws_events_targets as _targets,
    aws_autoscaling as _autoscaling,
)
from constructs import Construct


config = {
    "bucket_name": "valheim-aws",
    "ami_name": "valheim-ami",
    "desired_capacity": 0,

    "vpc_cidr": "10.0.0.0/24",
    "subnet_cidr_mask": 28,
    "instance_type": "t3a.medium",
    "instance_storage_gb": 15,
}


class ValheimAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket = self.configure_s3_bucket()
        self.configure_asg(s3_bucket)
        self.configure_event_bridge()
        self.configure_lambda()

    def configure_s3_bucket(self) -> _s3.Bucket:
        return _s3.Bucket(
            self, "ValheimS3Bucket",
            bucket_name=config["bucket_name"],
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

    def configure_asg(self, s3_bucket: _s3.Bucket):
        valheim_vpc = _ec2.Vpc(
            self, "ValheimVpc",
            cidr=config["vpc_cidr"],
            subnet_configuration=[
                _ec2.SubnetConfiguration(
                    cidr_mask=config["subnet_cidr_mask"],
                    name="public-subnet",
                    subnet_type=_ec2.SubnetType.PUBLIC,
                )
            ]
        )

        security_group = _ec2.SecurityGroup(
            self, "Ec2SecurityGroup",
            allow_all_outbound=True,
            vpc=valheim_vpc,
        )
        security_group.add_ingress_rule(
            peer=_ec2.Peer.any_ipv4(),
            connection=_ec2.Port.all_traffic()
        )

        ec2_role = _iam.Role(
            self, "ValheimEC2Role",
            assumed_by=_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
            ],
            inline_policies={
                "AutoscalingLifecycleHook": _iam.PolicyDocument(
                    statements=[
                        _iam.PolicyStatement(
                            effect=_iam.Effect.ALLOW,
                            actions=[
                                "autoscaling:CompleteLifecycleAction",
                                "autoscaling:DescribeAutoScalingInstances"
                            ],
                            resources=[
                                "*"
                            ]
                        )
                    ]
                )
            }
        )
        s3_bucket.grant_read_write(ec2_role)

        asg = _autoscaling.AutoScalingGroup(
            self, "ValheimASG",
            vpc=valheim_vpc,

            min_capacity=0,
            max_capacity=1,
            desired_capacity=config["desired_capacity"],

            key_name="main",
            security_group=security_group,
            instance_type=_ec2.InstanceType(config["instance_type"]),

            update_policy=_autoscaling.UpdatePolicy.rolling_update(
                min_success_percentage=0,
                min_instances_in_service=0,
            ),

            role=ec2_role,
            machine_image=_ec2.MachineImage.lookup(name=config["ami_name"]),

            block_devices=[
                _autoscaling.BlockDevice(
                    device_name="/dev/xvda",
                    volume=_autoscaling.BlockDeviceVolume.ebs(
                        config["instance_storage_gb"],
                        volume_type=_autoscaling.EbsDeviceVolumeType.GP3
                    )
                )
            ],

            init=_ec2.CloudFormationInit.from_config_sets(
                config_sets={
                    "default": ["EnableAnsibleYumPkg", "ConfigureInstance"]
                },
                configs={
                    "EnableAnsibleYumPkg": _ec2.InitConfig([
                        _ec2.InitPackage.apt("htop"),
                    ]),
                    "ConfigureInstance": _ec2.InitConfig([

                        _ec2.InitCommand.shell_command(
                            'su ubuntu -c "aws s3 cp s3://valheim-aws/ ./s3_files/ --recursive"',
                            cwd="/home/ubuntu"
                        ),
                        _ec2.InitCommand.shell_command(
                            'su ubuntu -c "chmod +x ./s3_files/*.sh"',
                            cwd="/home/ubuntu",
                        ),
                        _ec2.InitCommand.shell_command(
                            'su ubuntu -c "./s3_files/start.sh"',
                            cwd="/home/ubuntu",
                        ),
                    ])
                }
            ),
            init_options=_autoscaling.ApplyCloudFormationInitOptions(
                config_sets=["default"],
                include_role=False,
                include_url=False,
                ignore_failures=True
            ),
            signals=_autoscaling.Signals.wait_for_count(
                count=int(config["desired_capacity"]),
                timeout=Duration.minutes(30)
            ),
        )

        asg.add_lifecycle_hook(
            id="TerminationHook",
            lifecycle_hook_name="TestHook",
            heartbeat_timeout=Duration.minutes(30),
            default_result=_autoscaling.DefaultResult.CONTINUE,
            lifecycle_transition=_autoscaling.LifecycleTransition.INSTANCE_TERMINATING,
        )

    def configure_event_bridge(self):
        eventbridge_role = _iam.Role(
            self, "EventBridgeInvokeRunCommand",
            assumed_by=_iam.ServicePrincipal("events.amazonaws.com"),
            inline_policies={
                "Amazon_EventBridge_Invoke_Run_Command": _iam.PolicyDocument(
                    statements=[
                        _iam.PolicyStatement(
                            effect=_iam.Effect.ALLOW,
                            actions=["ssm:SendCommand"],
                            resources=[
                                "arn:aws:ssm:eu-west-2:*:document/AWS-RunShellScript"
                            ]
                        ),
                        _iam.PolicyStatement(
                            effect=_iam.Effect.ALLOW,
                            actions=["ssm:SendCommand"],
                            resources=[
                                "arn:aws:ec2:eu-west-2:590624982938:instance/*"
                            ],
                            conditions={
                                "StringEquals": {
                                    "ec2:ResourceTag/*": [
                                        "ValheimAws/ValheimASG"
                                    ]
                                }
                            }
                        )
                    ]
                )
            }
        )

        commands = [
            "su - ubuntu -c './s3_files/backup.sh'",
            "INSTANCE_ID=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`",
            "REGION=`wget -q -O - http://169.254.169.254/latest/meta-data/placement/region`",
            "ASG_NAME=`aws autoscaling describe-auto-scaling-instances --region $REGION --instance-ids $INSTANCE_ID | jq -r .AutoScalingInstances[0].AutoScalingGroupName`",
            "LIFECYCLE_NAME=\"TestHook\"",
            "aws autoscaling complete-lifecycle-action --lifecycle-action-result CONTINUE --region $REGION --lifecycle-hook-name $LIFECYCLE_NAME --auto-scaling-group-name $ASG_NAME --instance-id $INSTANCE_ID"
        ]

        # Had to use `CfnRule` because cdk provides no built-in construct for running a command via SSM
        # https://github.com/aws/aws-cdk/issues/7710
        _eventbridge.CfnRule(
            self, "AsgLifecycleCfnRule",
            event_pattern={
                "source": ["aws.autoscaling"],
                "detail-type": ["EC2 Instance-terminate Lifecycle Action"]
            },
            targets=[
                {
                    "id": "1",
                    "arn": "arn:aws:ssm:eu-west-2::document/AWS-RunShellScript",
                    "roleArn": eventbridge_role.role_arn,
                    "input": json.dumps({
                        "commands": commands,
                        "workingDirectory": ["/home/ubuntu"],
                        "executionTimeout": ["3600"]
                    }),
                    "runCommandParameters": {
                        "runCommandTargets": [{"key": "tag:Name", "values": ["ValheimAws/ValheimASG"]}],
                    }
                }
            ],
        )

    def configure_lambda(self):

        valheim_lambda = _lambda.Function(
            self, "ValheimLambda",
            description="Valheim game server controller",

            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='handler.lambda_handler',
            code=_lambda.Code.from_asset('lambda'),

            timeout=Duration.minutes(1),
            memory_size=512,
        )

        valheim_function_url = valheim_lambda.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )
        CfnOutput(self, "ValheimFunctionUrl", value=valheim_function_url.url)

        valheim_lambda.add_to_role_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=[
                    "autoscaling:UpdateAutoScalingGroup",
                ],
                resources=[
                    f"arn:aws:autoscaling:{Stack.of(self).region}:{Stack.of(self).account}:autoScalingGroup:*:autoScalingGroupName/*"
                ]
            )
        )
        valheim_lambda.add_to_role_policy(
            _iam.PolicyStatement(
                effect=_iam.Effect.ALLOW,
                actions=[
                    "ec2:DescribeInstances",
                    "autoscaling:DescribeAutoScalingGroups",
                    "autoscaling:DescribeAutoScalingInstances",
                ],
                resources=["*"]
            )
        )

        _eventbridge.Rule(
            self, "ShutdownValheimServerRule",
            rule_name="ShutdownValheimServer",
            description="Shuts down the game server every night at 3AM, preventing additional costs",

            schedule=_eventbridge.Schedule.cron(
                minute="00",
                hour="03"
            ),
            targets=[
                _targets.LambdaFunction(
                    valheim_lambda,
                    event=_eventbridge.RuleTargetInput.from_object(
                        {
                            "queryStringParameters": {
                                "action": "stop"
                            }
                        })
                )
            ]
        )
