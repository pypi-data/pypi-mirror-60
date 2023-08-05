from typing import Dict, Any, List, Optional
from aws_cdk.aws_ec2 import SecurityGroup, Subnet, Vpc, SubnetSelection
from aws_cdk.aws_iam import Role
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Construct, Duration


class LambdaFunction:
    """
    Class which creates AWS Lambda function CF definition with AWS CDK.
    """
    def __init__(
            self,
            scope: Construct,
            prefix: str,
            description: str,
            memory: int,
            timeout: int,
            handler: str,
            runtime: Runtime,
            role: Role,
            env: Dict[Any, Any],
            security_groups: List[SecurityGroup],
            subnets: List[Subnet],
            vpc: Vpc,
            source_code: Optional[Code] = None,
            **kwargs
    ) -> None:
        """
        Constructor.

        :param scope: A scope (CF template) in which this resource should be placed.
        :param prefix: Prefix string for function name.
        :param description: Function description.
        :param memory: Memory units (e.g. 128, 256, 512...) for the function.
        :param timeout: Time in seconds after which a function will be halted.
        :param handler: Method name of the function to call.
        :param runtime: Runtime environment (e.g. python3.6, nodejs10.0).
        :param role: Role to attach to the function.
        :param env: OS-level environment variables for the function.
        :param security_groups: Security groups for the function.
        :param subnets: Subnets in which the function lives. Note, subnets must have NAT Gateway.
        :param vpc: A VPC to put this lambda into.
        :param source_code: Code to include in this resource.
        :param kwargs: Other custom parameters.
        """
        self.lambda_function = Function(
            scope=scope,
            id=prefix + "Lambda",
            code=source_code or Code().inline(code=' '),
            handler=handler,
            runtime=runtime,
            allow_all_outbound=False,
            description=description,
            environment=env,
            function_name=prefix + 'Lambda',
            memory_size=memory,
            role=role,
            security_groups=security_groups,
            timeout=Duration.seconds(timeout),
            vpc=vpc,
            vpc_subnets=SubnetSelection(
                subnets=subnets
            ),
            **kwargs
        )
