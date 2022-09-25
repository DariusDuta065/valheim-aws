import aws_cdk as core
import aws_cdk.assertions as assertions

from valheim_aws.valheim_aws_stack import ValheimAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in valheim_aws/valheim_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ValheimAwsStack(app, "valheim-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
