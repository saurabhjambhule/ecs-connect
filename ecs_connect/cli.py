""" Wrapper script for awscli which connects to containers running in
    ecs seamlessly """
import click
import logging
import os
import re
import inquirer
import signal
from ecs_connect.version import __version__
from ecs_connect.config import ECSConfig
from ecs_connect.ecs import ECSHandler
from ecs_connect.ssm import SSMHandler
from configparser import RawConfigParser

@click.command()
@click.option('--profile', help="Name of the profile to use in ~/.ecs-connect. \
If none is provided, then the default profile will be used.\n")
@click.option('--awsprofile', help="Name of the aws profile to use form ecs-connect. \
If none is provided, then the default aws profile will be used.\n")
@click.option('--cluster', help="Name of the ECS cluster. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--service', help="Name of the service. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--task', help="Name of the task. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--exec_cmd', help="Initilization command to run with ecs exec. \
If provided, then parameter from profile will be overridden.\n")
@click.option('--container', help="Name of the container. \
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
@click.option('-i', '--interactive', is_flag=True, help='Interactive mode')
def main(profile, awsprofile, cluster, service, task, container, bastion, exec_cmd, cmd, all, version, verbose, debug, interactive):
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

    if not interactive:
        ecs_config = ECSConfig(logger)
        if not profile:
            profile = "default"
        if not cluster:
            cluster = ecs_config.get_cluster(profile)
        if not awsprofile:
            awsprofile = ecs_config.get_awsprofile(profile)
        if not task:
            task = ecs_config.get_task(profile)
        if not exec_cmd:
            exec_cmd = ecs_config.get_exec_cmd(profile)
        if not container:
            container = ecs_config.get_container(profile, exec_cmd)
        if task is None:
            if not service:
                service = ecs_config.get_service(profile)
        else:
            service = None
        if not bastion:
            bastion = ecs_config.get_bastion(profile)
        if not cmd:
            cmd = ecs_config.get_cmd(profile, exec_cmd)
        ssh_user = ecs_config.get_ssh_user(profile)
        ssh_key = ecs_config.get_ssh_key(profile)
        ssh_port = ecs_config.get_ssh_port(profile)

        ecs = ECSHandler(awsprofile, cluster, service, task, container, bastion, logger, cmd, exec_cmd)
        if exec_cmd is not None:
            ecs.exec()
        else:
            instance_id, bastion_enabled = ecs.get_ec2_instance_id()
            ssm = SSMHandler(awsprofile, instance_id, service, bastion_enabled, bastion, ssh_user, ssh_key, ssh_port, logger)
            ssm.run(cmd, all)
    else:
        config_path = os.path.expanduser('~') + '/.aws/config'
        _value = RawConfigParser()
        _value.read(config_path)
        aws_profiles = _value.sections()
        profiles = map( str, aws_profiles)
        profiles = list(map( lambda x: re.sub("profile ", "", x), profiles))
        questions = [
            inquirer.List('aws',
                        message="Select AWS Profile",
                        choices=profiles,
                    ),
        ]
        answers = inquirer.prompt(questions)
        ecs = ECSHandler(answers["aws"], '', '', '', '', '', logger, '', 'bash')
        ecs.interactive()

if __name__ == "__main__":
    main()
