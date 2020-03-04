"""Main module."""

import boto3


class ECSHandler():
    """ ECS handler  """
    def __init__(self, cluster, service, logger):
        self.cluster = cluster
        self.service = service
        self.logger = logger
        self.ecs_client = boto3.client('ecs')

    def get_task_id(self):
        response = self.ecs_client.list_tasks(
            cluster=self.cluster,
            serviceName=self.service,
            desiredStatus='RUNNING'
        )
        self.logger.info("Retrived task id using service and cluster name"
                         % response['taskArns'][0])
        return response['taskArns'][0]

    def get_container_instance_id(self):
        task_id = self.get_task_id()
        response = self.ecs_client.describe_tasks(
            cluster=self.cluster,
            tasks=[
                task_id,
            ]
        )
        self.logger.info("Retrived ecs container instance id using task id"
                         % response['tasks'][0]['containerInstanceArn'])
        return response['tasks'][0]['containerInstanceArn']

    def get_ec2_instance_id(self):
        container_instance_id = self.get_container_instance_id()

        response = self.ecs_client.describe_container_instances(
            cluster=self.cluster,
            containerInstances=[
                container_instance_id,
            ]
        )
        self.logger.info("Retrived ec2 instance id using container \
        instance id " % response['containerInstances'][0]['ec2InstanceId'])
        return response['containerInstances'][0]['ec2InstanceId']
