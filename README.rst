===========
ECS Connect
===========


.. image:: https://img.shields.io/pypi/v/ecs_connect.svg
        :target: https://pypi.python.org/pypi/ecs_connect


Seamlessly connect to containers running in ECS.

Requirements
------------
EC2 Based
#########
For EC2 based ECS deploymnets, you need SSM Session Manager enabled on the EC2 instances. For enabling SSM Sessions refer `this. <https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started.html>`__

Make sure you have set proper IAM permissions for the developer going to access containers deployed in EC2 using ecs-connect tool.

Fargate Based
##############
For Fargate based ECS deploymnets, the SSM Session Manager can't be enabled directly as undelying EC2 instances are managed by AWS. So a Bastion node, an EC2 instances with SSM Session Manager enabled is required. For enabling SSM Sessions refer `this. <https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started.html>`__

Also, the SSHD must be installed on the container to which you want to connect. And you need to create SSH keys and place them in the container and the bastion node. To setup SSH keys refer `this. <https://linuxize.com/post/how-to-setup-passwordless-ssh-login/>`_ Make sure you have placed SSH key in bastion node at **home/ssm-user/bastion** (where *bastion* is a key name)

Usage
--------
``ecs_connect --profile <profile> --cluster <cluster name> --service <service name> --cmd <init cmd>``


Example
--------
``ecs_connect``

If nothing is provided, then config will be pulled from default profile saved in ~/.ecs_connect config file.

Optional flags:

* **--profile** Name of the profile to use in ~/.ecs-connect. If none is provided, then the default profile will be used.
* **--cluster** Name of the ECS cluster.
* **--service** Name of the service.
* **--task** Started by name. If provided, the service will be ignored.
* **--cmd** Initilization command to run, will be executed once connected to container. If provided, then parameter from profile will be overridden.
* **--all** Displays all running containers, for ECS EC2 based running tasks/services.
* **--verbose** More verbose output.
* **--debug** Very verbose output. Useful for debugging.


Note
--------

* Set **cmd** to **sh** or **bash** depending on container os to get shell access.
* <service name> will be used to filter containers.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
