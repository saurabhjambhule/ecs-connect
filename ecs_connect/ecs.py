"""Main module."""

import boto3


class ECSHandler():
    """ ECS handler  """
    def __init__(self, cluster, service, task, bastion, logger):
        self.cluster = cluster
        self.service = service
        self.task = task
        self.bastion = bastion
        self.logger = logger
        self.ecs_client = boto3.client('ecs')

    def get_task_id(self):
        taskId = None
        if self.task:
            response = self.ecs_client.list_tasks(
                cluster=self.cluster,
                startedBy=self.task,
                desiredStatus='RUNNING'
            )
            self.logger.info("Retrived task id using task and cluster name: %s"
                             % response['taskArns'][0])
            taskId = response['taskArns'][0]
        else:
            response = self.ecs_client.list_tasks(
                cluster=self.cluster,
                serviceName=self.service,
                desiredStatus='RUNNING'
            )
            if response['taskArns'] == []:
                self.logger.error(
                    "No task running for <%s> service in <%s> cluster", self.service,
                     self.cluster
                )
                exit(1)

            ### todo: address multiple task running for single service
            self.logger.info("Retrived task id using service and cluster name: %s"
                             % response['taskArns'][0])
            taskId = response['taskArns'][0]

        return taskId

    def get_container_instance_id(self):
        task_id = self.get_task_id()
        response = self.ecs_client.describe_tasks(
            cluster=self.cluster,
            tasks=[
                task_id,
            ]
        )

        if response['tasks'][0]['launchType'] == 'FARGATE':
            if self.bastion == None:
                self.logger.error(
                    "Bastion node rquired for task running in FARGATE"
                )
                exit(1)

            return response['tasks'][0]['containers'][0]['networkInterfaces'][0]['privateIpv4Address'], 'FARGATE'

        self.logger.info("Retrived ecs container instance id using task id: %s"
                         % response['tasks'][0]['containerInstanceArn'])
        return response['tasks'][0]['containerInstanceArn'], 'EC2'

    def get_ec2_instance_id(self):
        container_instance_id, platform = self.get_container_instance_id()

        if platform == 'FARGATE':
            self.logger.info("Task is running in FARGATE, connecting using \
                            bastion node: %s" % self.bastion)
            return container_instance_id, True

        response = self.ecs_client.describe_container_instances(
            cluster=self.cluster,
            containerInstances=[
                container_instance_id,
            ]
        )
        self.logger.info("Retrived ec2 instance id using container \
        instance id: %s" % response['containerInstances'][0]['ec2InstanceId'])
        return response['containerInstances'][0]['ec2InstanceId'], False
