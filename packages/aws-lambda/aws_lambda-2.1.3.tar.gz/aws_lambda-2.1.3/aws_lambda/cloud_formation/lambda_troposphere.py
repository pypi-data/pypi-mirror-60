from typing import List, Any, Dict, Optional
from troposphere import GetAtt, Template, Ref
from troposphere.awslambda import Code, Function, VPCConfig, Environment
from troposphere.ec2 import SecurityGroup, Subnet
from troposphere.iam import Role


class LambdaFunction:
    """
    Class which creates AWS Lambda function CF definition with Troposphere library.
    """
    def __init__(
            self,
            prefix: str,
            description: str,
            memory: int,
            timeout: int,
            handler: str,
            runtime: str,
            role: Role,
            env: Dict[Any, Any],
            security_groups: List[SecurityGroup],
            subnets: List[Subnet],
            code: Optional[Code] = None,
            **kwargs
    ) -> None:
        """
        Constructor.

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
        :param source_code: Code to include in this resource.
        :param kwargs: Other custom parameters.
        """
        self.lambda_function = Function(
            prefix + "Lambda",
            Code=code or Code(ZipFile=' '),
            Handler=handler,
            Role=GetAtt(role, "Arn"),
            Runtime=runtime,
            MemorySize=memory,
            FunctionName=prefix + 'Lambda',
            Timeout=timeout,
            Environment=Environment(
                Variables=env
            ),
            Description=description,
            VpcConfig=VPCConfig(
                SecurityGroupIds=[Ref(sg) for sg in security_groups],
                SubnetIds=[Ref(sub) for sub in subnets]
            ),
            **kwargs
        )

    def add(self, template: Template) -> None:
        """
        Adds all created resources to a template.

        :param template: Template to which resources should be added.

        :return: No return.
        """
        template.add_resource(self.lambda_function)
