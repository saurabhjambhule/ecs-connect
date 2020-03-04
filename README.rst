===========
ECS Connect
===========


.. image:: https://img.shields.io/pypi/v/ecs_connect.svg
        :target: https://pypi.python.org/pypi/ecs_connect

.. image:: https://img.shields.io/travis/saurabhjambhule/ecs_connect.svg
        :target: https://travis-ci.com/saurabhjambhule/ecs_connect




Seamlessly connect to containers running in ECS.


Usage
--------
`ecs-connect --profile <profile> --cluster <cluster name> --service <service name> --cmd <init cmd>`


Example
--------
`ecs-connect`

If nothing is provided, then config will be pulled from default profile saved in ~/.ecs_connect config file.

Optional flags:
- `--profile` Name of the profile to use in ~/.ecs-connect. If none is provided, then the default profile will be used.
- `--cluster` Name of the ECS cluster. If provided, then parameter from profile will be overridden.
- `--service` Name of the service. If provided, then parameter from profile will be overridden.
- `--cmd` Initilization command to run, will be executed once connected to container. If provided, then parameter from profile will be overridden.
- `--all` Displays all running containers.
- `--verbose` More verbose output.
- `--debug` Very verbose output. Useful for debugging.


Note
--------

* Set `cmd` to `sh` or `bash` depending on container os to get shell access.
* <service name> will be used to filter containers.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
