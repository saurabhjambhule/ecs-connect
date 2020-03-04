""" Wrapper script for awscli which connects to containers running in ecs seamlessly """
import sys
import click
import logging
import os
from ecs_connect.version import __version__
from ecs_connect.config import ECSConfig
from ecs_connect.ecs import ECSHandler
from ecs_connect.ssm import SSMHandler

@click.command()
@click.option('--profile', help="Name of the profile to use in .ecs-connect. \
If none is provided, then the default profile will be used.\n")
@click.option('--cluster', help="Name of the ECS cluster. \
If provided, then the profile will be ignored.\n")
@click.option('--service', help="Name of the service. \
If provided, then the profile will be ignored.\n")
@click.option('-V', '--version', is_flag=True, help='Displays version number\n')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-d', '--debug', is_flag=True, help='Enables debug mode')
def main(profile, cluster, service, version, verbose, debug):
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

    if not profile:
        profile = "default"

    if cluster and not service:
        logger.error("service parameter is missing.")
    if not cluster and service:
        logger.error("cluster parameter is missing.")

    if not cluster and not service:
        ecs_config = ECSConfig(logger)
        cluster = ecs_config.get_cluster(profile)
        service = ecs_config.get_service(profile)
        cmd = ecs_config.get_cmd(profile)

    ecs = ECSHandler(cluster, service, logger)
    instance_id = ecs.get_ec2_instance_id()


    ssm = SSMHandler(instance_id, logger)
    ssm.run(cmd)

if __name__ == "__main__":
    main()
