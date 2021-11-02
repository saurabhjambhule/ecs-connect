"""Main module."""

import boto3
import subprocess
import time


class SSMHandler():
    """ SSM handler  """
    def __init__(self, awsprofile, ec2_id, service, bastion_enabled, bastion_id, ssh_user, ssh_key, ssh_port, logger):
        self.awsprofile = awsprofile
        self.ec2_id = ec2_id
        self.service = service
        self.bastion_enabled = bastion_enabled
        self.bastion_id = bastion_id
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.ssh_port = ssh_port
        self.logger = logger

        self.ssm_client = boto3.session.Session(profile_name=self.awsprofile).client('ssm')

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
        command = f'aws --profile {self.awsprofile} ssm start-session --target {self.ec2_id} \
        --document-name AWS-StartInteractiveCommand \
        --parameters command="sudo docker exec -it {container_id} {exec_cmd}"'
        self.logger.info("Running: %s", command)

        subprocess.call(command, shell=True)

    def start_bastion_session(self, exec_cmd):
        command = f'aws --profile {self.awsprofile} ssm start-session --target {self.bastion_id} \
        --document-name AWS-StartInteractiveCommand \
        --parameters command="ssh -i {self.ssh_key} -p {self.ssh_port} {self.ssh_user}@{self.ec2_id}"'
        self.logger.info("Running: %s", command)

        subprocess.call(command, shell=True)

    def run_directly(self, exec_cmd, all):
        container_id = self.get_conatiners(all)
        self.start_session(container_id, exec_cmd)

    def run_through_bastion(self, exec_cmd, all):
        self.start_bastion_session(exec_cmd)

    def run(self, exec_cmd, all):
        if self.bastion_enabled:
            self.run_through_bastion(exec_cmd, all)
        else:
            self.run_directly(exec_cmd, all)
