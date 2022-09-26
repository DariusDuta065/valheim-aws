import json
import boto3

client = boto3.client('autoscaling')

def lambda_handler(event, context):
    desired_capacity = 0

    try:
        assert "queryStringParameters" in event, "wrong event type provided, use function url"
        assert "desired_capacity" in event["queryStringParameters"], "desired_capacity not specified"
        
        desired_capacity = int(event["queryStringParameters"]["desired_capacity"])
        assert 0 <= desired_capacity <= 1, "desired_capacity must be 0 or 1"
    except Exception as e:
        print(e)
        return { 'statusCode': 401, 'message': 'aici' }
    
    try:
        res = client.update_auto_scaling_group(
            AutoScalingGroupName=get_asg_name(),
            DesiredCapacity=desired_capacity
        )
        print(res)
    except Exception as e:
        return {
            'statusCode': 500,
            'message': e.response['Error']['Message']
        }

    return {
        'statusCode': 200,
        'message': 'Success'
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
    
    if "AutoScalingGroups" not in asgs or len(asgs["AutoScalingGroups"]) < 1:
        return {
            'statusCode': 500,
            'message': 'Failure'
        }
    return asgs["AutoScalingGroups"][0]["AutoScalingGroupName"]
