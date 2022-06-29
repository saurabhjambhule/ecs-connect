""" Config helper """

import os
from configparser import RawConfigParser


class ECSConfig():
    """ Config handler class """
    def __init__(self, logger):
        self.logger = logger
        self.config_path = os.path.expanduser('~') + '/.ecs_connect'
        self._value = RawConfigParser()
        self._value.read(self.config_path)

    def get_cluster(self, profile):
        """ Gets ECS cluster from config """
        if self._value.has_option(profile, 'cluster'):
            if self._value.has_option(profile, 'cluster'):
                cluster = self._value.get(profile, 'cluster')
                self.logger.info("Connecting to: %s cluster" % cluster)
            else:
                self.logger.error(
                    "No cluster parameter found"
                )
                exit(1)
        else:
            self.logger.error(
                "No profile found. Please define a default profile, \
                or specify a named profile using `--profile`"
            )
            exit(1)
        return cluster

    def get_awsprofile(self, profile):
        """ Gets AWS profile from config """
        awsprofile = None
        if self._value.has_option(profile, 'awsprofile'):
            awsprofile = self._value.get(profile, 'awsprofile')
        else:
            awsprofile = "default"
        self.logger.info("%s is selected as awsprofile" % awsprofile)
        return awsprofile

    def get_service(self, profile):
        """ Gets service from config """
        service = None
        if self._value.has_option(profile, 'service'):
            service = self._value.get(profile, 'service')
        else:
            self.logger.error(
                "No service parameter found"
            )
            exit(1)
        self.logger.info("%s is selected for connection" % service)
        return service

    def get_exec_cmd(self, profile):
        """ Gets task from config """
        exec_cmd = None
        if self._value.has_option(profile, 'exec_cmd'):
            exec_cmd = self._value.get(profile, 'exec_cmd')

        self.logger.info("%s is selected as exec cmd" % exec_cmd)
        return exec_cmd

    def get_task(self, profile):
        """ Gets task from config """
        task = None
        if self._value.has_option(profile, 'task'):
            task = self._value.get(profile, 'task')

        self.logger.info("%s is selected as task" % task)
        return task

    def get_container(self, profile, exec_cmd):
        """ Gets container name from config """
        container = None
        if self._value.has_option(profile, 'container'):
            container = self._value.get(profile, 'container')
        elif exec_cmd is not None:
            self.logger.error(
                "No container parameter found"
            )
            exit(1)

        self.logger.info("%s is selected as container" % container)
        return container

    def get_bastion(self, profile):
        """ Gets bastion node id from config """
        bastion = None
        if self._value.has_option(profile, 'bastion'):
            bastion = self._value.get(profile, 'bastion')

        self.logger.info("%s is selected as bastion node" % bastion)
        return bastion

    def get_cmd(self, profile, exec_cmd):
        """ Gets init command from config """
        cmd = None
        if self._value.has_option(profile, 'cmd'):
            cmd = self._value.get(profile, 'cmd')
        elif exec_cmd is None:
            self.logger.error(
                "No cmd parameter found"
            )
            exit(1)
        self.logger.info("%s is selected as initilization command" % cmd)
        return cmd

    def get_ssh_user(self, profile):
        """ Gets ssh user name from config """
        ssh_user = 'root'
        if self._value.has_option(profile, 'ssh_user'):
            ssh_user = self._value.get(profile, 'ssh_user')
        self.logger.info("%s is selected as a ssh user" % ssh_user)
        return ssh_user

    def get_ssh_key(self, profile):
        """ Gets ssh key path from config """
        ssh_key = '/home/ssm-user/bastion'
        if self._value.has_option(profile, 'ssh_key'):
            ssh_key = self._value.get(profile, 'ssh_key')
        self.logger.info("%s is selected as a ssh user" % ssh_key)
        return ssh_key

    def get_ssh_port(self, profile):
        """ Gets ssh key path from config """
        ssh_port = '22'
        if self._value.has_option(profile, 'ssh_port'):
            ssh_port = self._value.get(profile, 'ssh_port')
        self.logger.info("%s is selected as a ssh port" % ssh_port)
        return ssh_port
