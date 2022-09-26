import json
import boto3

client = boto3.client('autoscaling')


def lambda_handler(event, context):
    action = "stop"

    try:
        assert "queryStringParameters" in event, "wrong event type provided, use function url & provide `action` in the query string"
        assert "action" in event["queryStringParameters"], "action not specified"
        assert event["queryStringParameters"]["action"] in [
            "status", "start", "stop"], "action must be: ['status', 'start', 'stop']"

        action = event["queryStringParameters"]["action"]
    except AssertionError as e:
        return {'statusCode': 400, 'body': {'message': str(e)}}
    except:
        return {'statusCode': 500}

    if action == "status":
        return get_status()
    return update_asg_capacity(action)


def update_asg_capacity(action: str):
    desired_capacity = 0 if action == "stop" else 1

    try:
        asg_name = get_asg_name()
    except:
        return {
            'statusCode': 500,
            'body': {'message': 'could not get ASG name'}
        }

    try:
        res = client.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=desired_capacity
        )
        print(res)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {'message': e.response['Error']['Message']}
        }

    return {
        'statusCode': 200,
        'body': {'message': 'success'}
    }


def get_asg_name() -> str:
    asgs = client.describe_auto_scaling_groups(
        MaxRecords=1,
        Filters=[
            {
                'Name': 'tag:project',
                'Values': [
                    'valheim',
                ]
            }
        ]
    )

    assert "AutoScalingGroups" in asgs
    assert len(asgs["AutoScalingGroups"]) > 0
    return asgs["AutoScalingGroups"][0]["AutoScalingGroupName"]


def get_status():
    ec2_client = boto3.client('ec2')

    try:
        res = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:project',
                    'Values': ['valheim']
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        )
        assert "Reservations" in res

        if len(res["Reservations"]) > 0:
            return {
                'statusCode': 200,
                'body': {
                    'status': 'started',
                    'ip': str(res["Reservations"][0]["Instances"][0]["PublicIpAddress"]),
                    'launch_time': str(res["Reservations"][0]["Instances"][0]["LaunchTime"])
                }
            }
        else:
            return {
                'statusCode': 200,
                'body': {'status': 'shutdown'},
            }

    except AssertionError as e:
        return {'statusCode': 500, 'body': {'message': str(e)}}
    except:
        return {'statusCode': 500}
