""" Wrapper script for awscli which connects to containers running in
    ecs seamlessly """
import click
import logging
import json
import os
import boto3
from configparser import RawConfigParser
from ecs_connect.version import __version__
from ecs_connect.config import ECSConfig
from ecs_connect.ecs import ECSHandler
from ecs_connect.ssm import SSMHandler


@click.command()
@click.option('--profile', help="Name of the profile to use in ~/.ecs-connect. \
If none is provided, then the default profile will be used.\n")
@click.option('--awsprofile', help="Name of the aws profile to use form ecs-connect. \
If none is provided, then the default aws profile will be used.\n")
@click.option('--nosso', is_flag=True, help="Enables/disable auth though aws sso")
@click.option('--cluster', help="Name of the ECS cluster. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--service', help="Name of the service. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--task', help="Name of the task. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--bastion', help="Instance Id of the bastion node, \
required for task running in FARGATE. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--cmd', help="Initilization command to run. \
If provided, then parameter from profile will be overridden.\n")
@click.option('-a', '--all', is_flag=True,
              help='Displays all running containers\n')
@click.option('-V', '--version', is_flag=True,
              help='Displays version number\n')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-d', '--debug', is_flag=True, help='Enables debug mode')
def main(profile, awsprofile, cluster, nosso, service, task, bastion, cmd, all, version, verbose, debug):
    if version:
        print(__version__)
        exit(0)

    # Set up logging
    logger = logging.getLogger('ecs-connect')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARN)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if verbose:
        handler.setLevel(logging.INFO)
    if debug:
        handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    ecs_config = ECSConfig(logger)
    if not profile:
        profile = 'default'
    if not cluster:
        cluster = ecs_config.get_cluster(profile)
    if not awsprofile:
        awsprofile = ecs_config.get_awsprofile(profile)
    if not task:
        task = ecs_config.get_task(profile)
    if task is None:
        if not service:
            service = ecs_config.get_service(profile)
    else:
        service = None
    if not bastion:
        bastion = ecs_config.get_bastion(profile)
    if not cmd:
        cmd = ecs_config.get_cmd(profile)

    session = auth(awsprofile, nosso)

    ecs = ECSHandler(session, cluster, service, task, bastion, logger)
    instance_id, bastion_enabled = ecs.get_ec2_instance_id()

    ssm = SSMHandler(session, instance_id, service, bastion_enabled, bastion, logger)
    ssm.run(cmd, all)

def auth(awsprofile, nosso):
    if nosso:
        session = boto3.Session(profile_name=awsprofile)
        return session

    sso_path = os.path.expanduser('~') + '/.aws/sso/cache'
    config_path = os.path.expanduser('~') + '/.aws/config'

    profile_config = RawConfigParser()
    profile_config.read(config_path)
    if not awsprofile == 'default':
        awsprofile = 'profile ' + awsprofile
    account_id = profile_config.get(awsprofile, 'sso_account_id')
    role_name = profile_config.get(awsprofile, 'sso_role_name')
    region = profile_config.get(awsprofile, 'region')

    json_files = [pos_json for pos_json in os.listdir(sso_path) if pos_json.endswith('.json')]
    for json_file in json_files :
        path = sso_path + '/' + json_file
        with open(path) as file :
            data = json.load(file)
            if 'accessToken' in data:
                accessToken = data['accessToken']

    client = boto3.client('sso', region_name=region)
    response = client.get_role_credentials(
        roleName=role_name,
        accountId=account_id,
        accessToken=accessToken
    )

    session = boto3.Session(aws_access_key_id=response['roleCredentials']['accessKeyId'], aws_secret_access_key=response['roleCredentials']['secretAccessKey'], aws_session_token=response['roleCredentials']['sessionToken'], region_name=region)
    return session

if __name__ == "__main__":
    main()
