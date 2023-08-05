from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup(
    name='aws_lambda',
    version='2.1.2',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    packages=find_packages(exclude=['venv', 'test']),
    description='Package which helps to do various actions associated with AWS Lambda functions.',
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'boto3',
        'botocore',
        'troposphere',
        'aws-cdk.core',
        'aws-cdk.aws_iam',
        'aws-cdk.aws_ec2',
        'aws-cdk.aws_lambda',
        'cfnresponse'
    ],
    author='Laimonas Sutkus',
    author_email='laimonas.sutkus@gmail.com',
    keywords='AWS CDK CloudFormation Troposphere Lambda Infrastructure Cloud DevOps DeploymentPackage',
    url='https://github.com/laimonassutkus/AwsLambda',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
)
