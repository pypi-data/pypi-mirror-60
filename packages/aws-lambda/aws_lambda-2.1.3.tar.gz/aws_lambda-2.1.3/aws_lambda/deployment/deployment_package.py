import os
import subprocess
import logging
import uuid

from typing import Optional
from aws_lambda.deployment import lambda_deployment_dir

logr = logging.getLogger(__name__)


class DeploymentPackage:
    """
    Deployment management class which creates a deployment package for a specified lambda project
    and uploads it to aws infrastructure.
    """
    def __init__(
            self,
            project_src_path: str,
            lambda_name: str,
            s3_upload_bucket: str,
            s3_bucket_region: str,
            aws_profile: str,
            environment: Optional[str] = None,
            refresh_lambda: bool = False
    ) -> None:
        """
        Constructor.

        :param project_src_path: Path to your lambda project.
        :param lambda_name: Name of the lambda function in your aws infrastructure.
        :param s3_upload_bucket: A bucket to which upload a deployment package.
        :param s3_bucket_region: A bucket region.
        :param aws_profile: Aws profile which is setup by running "aws configure" on your computer.
        :param environment: Project environment (dev or prod).
        :param refresh_lambda: A flag specifying whether to call update-function after uploading
        a deployment package to a S3 bucket.
        """
        self.__refresh_lambda = refresh_lambda
        self.__aws_profile = aws_profile
        self.__environment = environment or ''
        self.__s3_upload_bucket = s3_upload_bucket
        self.__s3_bucket_region = s3_bucket_region
        self.__project_src_path = project_src_path
        self.__lambda_name = lambda_name
        self.__dir = lambda_deployment_dir

        # Generate a semi-random path for a deployment package for this session.
        self.__root = f'/tmp/aws-lambda/lambda/deployment/{str(uuid.uuid4())}'
        self.__root_build = '{}/package.zip'.format(self.__root)

        self.__build_command = [
            os.path.join(self.__dir, 'lambda_build.sh'),
            self.__environment,
            self.__project_src_path,
            self.__root,
            self.__root_build
        ]

        upload_options = ['-s']
        if self.__refresh_lambda:
            upload_options.append('-l')

        self.__upload_command = [
            os.path.join(self.__dir, 'lambda_upload.sh'),
            self.__lambda_name,
            self.__s3_upload_bucket,
            self.__aws_profile,
            self.__s3_bucket_region,
            self.__root_build
        ]

        self.__upload_command.extend(upload_options)

    def deploy(self) -> None:
        """
        Build and deploys a lambda project.

        :return: No return.
        """
        # Actually we do not have to check what type of environment is passed. The script will assert this
        # part and throw an exception if the value is not valid. However this is purely optimization part
        # which would save quite some time if an incorrect environment is provided. If installation
        # scripts tend to change and support more environments - delete or update the line below.
        assert self.__environment in ['dev', 'prod', 'none'], 'Unsuppored env!'

        try:
            # Firstly, lets install and build the package.
            logr.info('Installing...')
            output = subprocess.check_output(self.__build_command, stderr=subprocess.STDOUT)
            logr.info(output.decode())

            # Secondly, upload and update deployment package.
            logr.info('Uploading...')
            output = subprocess.check_output(self.__upload_command, stderr=subprocess.STDOUT)
            logr.info(output.decode())
        except subprocess.CalledProcessError as ex:
            logr.error(ex.output.decode())
            raise
