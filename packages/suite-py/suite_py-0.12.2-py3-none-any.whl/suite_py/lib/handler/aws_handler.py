from __future__ import print_function, unicode_literals
from ..logger import Logger
from distutils.version import StrictVersion
import sys
import boto3

logger = Logger()

s3 = boto3.resource('s3')
cloudformation = boto3.client('cloudformation')
cloudfront = boto3.client('cloudfront')


def update_stack(stack_name, version):
    params = get_template_params(stack_name, version)
    if params:
        logger.info(
            "Effettuo update template cloudformation {}".format(stack_name))
        response = cloudformation.update_stack(
            StackName=stack_name,
            TemplateBody=get_template_from_stack_name(stack_name),
            Parameters=params
        )
    else:
        logger.error(
            "Nessun parametro trovato sullo stack {}".format(stack_name))
        sys.exit(-1)


def get_template_params(stack_name, version):
    parameters = get_parameters_from_stack_name(stack_name)

    for param in parameters:
        if param["ParameterKey"] == "ReleaseVersion":
            parameters[parameters.index(
                param)]["ParameterValue"] = str(version)
            return parameters
        else:
            continue

    return None


def get_parameters_from_stack_name(stack_name):
    return cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["Parameters"]


def get_stacks_name(repo):
    stacks_name = []
    base_stacks_name = ["ecs-task-{}-production".format(repo),
                        "ecs-task-{}-vpc-production".format(repo),
                        "ecs-job-{}-production".format(repo)]

    for stack_name in base_stacks_name:
        if stack_exists(stack_name):
            stacks_name.append(stack_name)

    return stacks_name


def stack_exists(stack_name):
    try:
        cloudformation.describe_stacks(StackName=stack_name)
        return True
    except:
        return False


def get_stack_stauts(stack_name):
    return cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"]


def get_artifacts_version_from_s3(repo):
    bucket_artifacts = s3.Bucket('prima-artifacts-encrypted')
    versions = []

    for bucket_object in bucket_artifacts.objects.filter(Prefix="microservices/{}".format(repo)):
        if '-production.tar.gz' in bucket_object.key:
            versions.append(bucket_object.key.split(
                "/")[2].replace('-production.tar.gz', ''))

    versions.sort(key=StrictVersion, reverse=True)
    return versions


def is_cloudfront_distribution(repo):
    distributions = cloudfront.list_distributions()[
        "DistributionList"]["Items"]
    for distribution in distributions:
        if "prima-prod-{}.s3.amazonaws.com".format(repo) == distribution["Origins"]["Items"][0]["DomainName"]:
            return True
        else:
            continue
    return False
