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

    def get_task(self, profile):
        """ Gets service from config """
        task = None
        if self._value.has_option(profile, 'task'):
            task = self._value.get(profile, 'task')

        self.logger.info("%s is selected as task" % task)
        return task

    def get_bastion(self, profile):
        """ Gets bastion node id from config """
        bastion = None
        if self._value.has_option(profile, 'bastion'):
            bastion = self._value.get(profile, 'bastion')

        self.logger.info("%s is selected as bastion node" % bastion)
        return bastion

    def get_cmd(self, profile):
        """ Gets init command from config """
        cmd = None
        if self._value.has_option(profile, 'cmd'):
            cmd = self._value.get(profile, 'cmd')
        else:
            self.logger.error(
                "No cmd parameter found"
            )
            exit(1)
        self.logger.info("%s is selected as initilization command" % cmd)
        return cmd
