"""Main module."""

import boto3
import subprocess
import re
import inquirer
import botocore

class ECSHandler():
    """ ECS handler  """
    def __init__(self, awsprofile, cluster, service, task, container, bastion, logger, cmd, exec_cmd):
        self.awsprofile = awsprofile
        self.cluster = cluster
        self.service = service
        self.container = container
        self.task = task
        self.bastion = bastion
        self.logger = logger
        self.cmd = cmd
        self.exec_cmd = exec_cmd

        try:
            self.ecs_client = boto3.session.Session(profile_name=self.awsprofile).client('ecs')
            test_connection = self.ecs_client.list_clusters(maxResults=1)
        except botocore.exceptions.UnauthorizedSSOTokenError as e:
            command = f'aws --profile {self.awsprofile} sso login'
            self.logger.info("Running: %s", command)
            subprocess.call(command, shell=True)

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
            if self.bastion == None and self.exec_cmd == None:
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

    def exec(self):
        cluster_response = self.ecs_client.list_clusters()
        cluster_regex = re.compile(".*" + self.cluster)
        clusters = list(filter(cluster_regex.match, cluster_response['clusterArns']))
        if not clusters:
            self.logger.error(
                "The <%s> cluster does not exists.", self.cluster
            )
            exit(1)

        service_response = self.ecs_client.list_services(
            cluster=self.cluster
        )
        if self.task is None:
            service_regex = re.compile(".*" + self.service)
            services = list(filter(service_regex.match, service_response['serviceArns']))
            if not services:
                self.logger.error(
                    "The <%s> service does not exists.", self.service
                )
                exit(1)
        task = self.get_task_id()
        command = f'aws --profile {self.awsprofile} --region us-east-1 \
        ecs execute-command \
        --cluster {self.cluster} --task {task} --container {self.container} \
        --command {self.exec_cmd} --interactive'
        self.logger.info("Running: %s", command)

        subprocess.call(command, shell=True)

    def interactive(self):
        cluster_response = self.ecs_client.list_clusters(maxResults=100)
        cluster_arns = cluster_response['clusterArns']
        if not cluster_arns:
            self.logger.error(
                "There are no ECS clusters."
            )
            exit(1)
        clusters = map( str, cluster_arns)
        clusters = list(map( lambda x: re.sub(".*:cluster/", '', x), clusters))
        questions = [
            inquirer.List('cluster',
                        message="Select Cluster",
                        choices=clusters,
                    ),
        ]
        answers = inquirer.prompt(questions)
        self.cluster = answers["cluster"]

        service_response = self.ecs_client.list_services(
                cluster=self.cluster,
                maxResults=100
            )
        service_arns = service_response['serviceArns']
        if not service_arns:
            self.logger.error(
                "There are no ECS services in %s cluster.", self.cluster
            )
            exit(1)
        services = map( str, service_arns)
        services = list(map( lambda x: re.sub(".*:service/" + self.cluster + "/", "", x), services))
        questions = [
            inquirer.List('service',
                        message="Select Service",
                        choices=services,
                    ),
        ]
        answers = inquirer.prompt(questions)
        self.service = answers["service"]

        task_response = self.ecs_client.list_tasks(
                cluster=self.cluster,
                serviceName=self.service,
                desiredStatus='RUNNING',
                maxResults=100
            )
        task_arns = task_response['taskArns']
        if not task_arns:
            self.logger.error(
                "There are no ECS tasks running in %s service.", self.service
            )
            exit(1)
        tasks = map( str, task_arns)
        tasks = list(map( lambda x: re.sub(".*:task/" + self.cluster + "/", "", x), tasks))
        questions = [
            inquirer.List('task',
                        message="Select Task ",
                        choices=tasks,
                    ),
        ]
        answers = inquirer.prompt(questions)
        self.task = answers["task"]

        container_response = self.ecs_client.describe_tasks(
                cluster=self.cluster,
                tasks=[self.task]
            )
        containers = []
        for name in container_response['tasks'][0]['containers']:
            containers.append(name['name'])
        questions = [
            inquirer.List('container',
                        message="Select Container",
                        choices=containers,
                    ),
        ]
        answers = inquirer.prompt(questions)
        self.container = answers["container"]

        command = f'aws --profile {self.awsprofile} --region us-east-1 \
        ecs execute-command \
        --cluster {self.cluster} --task {self.task} --container {self.container} \
        --command {self.exec_cmd} --interactive'
        self.logger.info("Running: %s", command)

        subprocess.call(command, shell=True)
