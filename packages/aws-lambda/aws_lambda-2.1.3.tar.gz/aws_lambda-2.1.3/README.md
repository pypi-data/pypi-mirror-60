## Aws Lambda
A package used to manage lambda functions.
With this package it is easy to create lambda deployment packages and 
create lambda resources with CloudFormation.

### Description

An AWS Lambda management library which makes some of the painful parts less painful.
E.g. This project makes it easy to create Lambda deployment packages and upload
them to S3. 

### Prerequisites

In order to operate the package, you must first install it, using:
 
 ```bash
pip install aws-lambda
```

### How to use

#### Making CloudFormation resources

##### With Troposphere

```python
# Create a Troposphere template.
from troposphere import Template

# Create the initial template.
template: Template = Template()

# Create some of the resources for lambda function resource.
from troposphere.iam import Role
from troposphere.ec2 import Subnet
from troposphere.ec2 import SecurityGroup

lambda_role = Role(...)
lambda_subnets = [Subnet(...)]
lambda_security_groups = [SecurityGroup(...)]

# Import a lambda function resource class.
from aws_lambda.cloud_formation.lambda_troposphere import LambdaFunction

# Create a lambda function resource.
lambda_function = LambdaFunction(
    prefix='MyCustomPrefix',
    description='My custom description.',
    memory=128,
    timeout=300,
    handler='file.function',
    runtime='python3.8',
    role=lambda_role,
    env={},
    security_groups=lambda_security_groups,
    subnets=lambda_subnets
)

# Add lambda function to a Troposphere template.
lambda_function.add(template)
```

##### With AWS CDK

```python
# Import AWS CDK core, iam, ec2, and lambda libraries.
from aws_cdk import core
from aws_cdk import aws_lambda
from aws_cdk import aws_iam
from aws_cdk import aws_ec2

# Create a CDK app.
app = core.App()

# Define a CDK stack class.
class MainStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Import lambda function resource class.
        from aws_lambda.cloud_formation.lambda_aws_cdk import LambdaFunction
        
        lambda_vpc = aws_ec2.Vpc(...)
        lambda_role = aws_iam.Role(...)
        lambda_security_groups = [aws_ec2.SecurityGroup(...)]
        lambda_subnets = [aws_ec2.Subnet(...)]
        
        # Create lambda function.
        LambdaFunction(
            scope=self,
            prefix='MyCustomPrefix',
            description='My custom description.',
            memory=128,
            timeout=300,
            handler='file.function',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            role=lambda_role,
            env={},
            security_groups=lambda_security_groups,
            subnets=lambda_subnets,
            vpc=lambda_vpc
        )

# Create stack instance.
MainStack(app, "MainStack")

# Create a CloudFormation template.
app.synth()
```

#### Making Lambda deployment packages.

```python
# Import deployment package manager class.
from aws_lambda.deployment.deployment_package import DeploymentPackage

# Suppose you have a project under a path:
SCR_PATH = '/home/user/projects/my_project'

# Suppose you have run 'aws configure' on your machine and have a default profile.
AWS_PROFILE = 'default'

# Create deployment manager instance.
deployment_package = DeploymentPackage(
    project_src_path=SCR_PATH,
    lambda_name='MyCoolLambda',
    s3_upload_bucket='MyCoolS3Bucket',
    s3_bucket_region='eu-west-1',
    aws_profile=AWS_PROFILE,
    environment='prod',
    refresh_lambda=True
)

# Initiate deployment.
deployment_package.deploy()
```
