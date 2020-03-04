"""Main module."""

import os
import boto3
import subprocess
import time

class SSMHandler():
    """ SSM handler  """
    def __init__(self, ec2_id, logger):
        self.ec2_id = ec2_id
        self.logger = logger
        self.ssm_client = boto3.client('ssm')

    def get_conatiners(self):
        response = self.ssm_client.send_command(
                    InstanceIds=[self.ec2_id],
                    DocumentName="AWS-RunShellScript",
                    Parameters={'commands': ['sudo docker ps']}, )
        command_id = response['Command']['CommandId']

        while True:
            time.sleep(1)
            output = self.ssm_client.get_command_invocation(
                  CommandId=command_id,
                  InstanceId=self.ec2_id,
                )
            if output['Status'] != "InProgress":
                break

        running_container = output['StandardOutputContent'].count('\n') - 1
        if running_container < 0:
            self.logger.error("No container running")

        if running_container == 1:
            lines = output['StandardOutputContent'].split('\n')
            conatiner_details = lines[1].split()
            return conatiner_details[0]

        print(output['StandardOutputContent'])
        container_id = input('Please enter conatiner id: ')
        return container_id

    def start_session(self, container_id, cmd):
        exec = f'aws ssm start-session --target {self.ec2_id} \
            --document-name AWS-StartInteractiveCommand \
            --parameters command="sudo docker exec -it {container_id} {cmd}"'
        self.logger.info("Running: %s", exec)

        returned_value = subprocess.call(exec, shell=True)

    def run(self, cmd):
        container_id = self.get_conatiners()
        self.start_session(container_id, cmd)
