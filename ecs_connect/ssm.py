"""Main module."""

import boto3
import subprocess
import time


class SSMHandler():
    """ SSM handler  """
    def __init__(self, ec2_id, service, logger):
        self.ec2_id = ec2_id
        self.service = service
        self.logger = logger
        self.ssm_client = boto3.client('ssm')

    def get_conatiners(self, all):
        if all:
            exec_cmd = f'sudo docker ps'
        else:
            exec_cmd = f'sudo docker ps -f name={self.service}'
        response = self.ssm_client.send_command(
                    InstanceIds=[self.ec2_id],
                    DocumentName="AWS-RunShellScript",
                    Parameters={'commands': [exec_cmd]}, )
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
        if running_container <= 0:
            self.logger.error("No container running with name %s.\
                \nUse --all/-a to display all running container.",
                              self.service)
            exit(1)

        if running_container == 1:
            lines = output['StandardOutputContent'].split('\n')
            conatiner_details = lines[1].split()
            return conatiner_details[0]

        print(output['StandardOutputContent'])
        container_id = input('Please enter conatiner id: ')
        return container_id

    def start_session(self, container_id, exec_cmd):
        command = f'aws ssm start-session --target {self.ec2_id} \
        --document-name AWS-StartInteractiveCommand \
        --parameters command="sudo docker exec -it {container_id} {exec_cmd}"'
        self.logger.info("Running: %s", command)

        subprocess.call(command, shell=True)

    def run(self, exec_cmd, all):
        container_id = self.get_conatiners(all)
        self.start_session(container_id, exec_cmd)
