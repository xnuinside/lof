
AWS Lambdas on FastAPI - LoF
----------------------------


.. image:: https://img.shields.io/pypi/v/lof
   :target: https://img.shields.io/pypi/v/lof
   :alt: badge1
 
.. image:: https://img.shields.io/pypi/l/lof
   :target: https://img.shields.io/pypi/l/lof
   :alt: badge2
 
.. image:: https://img.shields.io/pypi/pyversions/lof
   :target: https://img.shields.io/pypi/pyversions/lof
   :alt: badge3

.. image:: https://github.com/xnuinside/lof/actions/workflows/main.yml/badge.svg
   :target: https://github.com/xnuinside/lof/actions/workflows/main.yml/badge.svg
   :alt: workflow


AWS Lambdas on FastAPI (LoF) is a command line tool that helps you fast & easy up & run your Python AWS Lambdas for tests and local development. 

Pay attention, that this is only for **Python lambdas**.

It does not support any other programming languages.

How does it work?
-----------------

Install
^^^^^^^

.. code-block:: bash


       pip install lof

Now run lof & provide to it path to your template yaml/json file.
Or you can run it from source dir with template.yaml (/.json) without any args

How to use
^^^^^^^^^^

.. code-block:: bash


       lof

       # or if path custom

       lof --template example/template.yaml

You can choose that lambdas exclude from run by passing their names:

.. code-block:: bash


       lof --template example/template.yaml --exclude=PostLambda2Function

To pass environment variables to Lambdas, use flag --env, you can pass variables in 2 formats - json format and '.env' format. Both files as examples presented in example/ folder

.. code-block:: bash


       lof --env=.env

       # or 

       lof --env=vars.json

Other settings
--------------

.. code-block:: text


       Usage: lof [OPTIONS]

       Options:
       --template TEXT                 Path to AWS Code Deploy template with
                                       lambdas  [default: template.yaml]

       --env TEXT                      Path to file with environment variables
       --exclude TEXT                  Exclude lambdas.FastAPI will not up & run
                                       them. Pass as string with comma. Example:
                                       PostTrafficHook,PretrafficHook.  [default: ]

       --port INTEGER                  Port to run lof  [default: 8000]
       --host TEXT                     Host to run lof  [default: 0.0.0.0]
       --workers INTEGER               Count of unicorn workers to run.If you want
                                       run more when 1 worker LoF will generate
                                       temp FastAPI server code for your lambdas.
                                       [default: 1]

       --debug / --no-debug            Debug flag for Uvicorn  [default: True]
       --reload / --no-reload          Reload flag for Uvicorn  [default: False]
       --install-completion [bash|zsh|fish|powershell|pwsh]
                                       Install completion for the specified shell.
       --show-completion [bash|zsh|fish|powershell|pwsh]
                                       Show completion for the specified shell, to
                                       copy it or customize the installation.

       --help                          Show this message and exit.

This mean, that lof will up & run all lambdas exclude this 2: PostTrafficHook & Roles

Demo
----

will be added soon

TODO
----


#. Add feature to call Authorizer & CORS lambdas handlers in local run.

Example
-------

To try how LoF works you can use AWS CloudFormation template.yaml & Lambdas from example/ folder.

Issues & features request
-------------------------

Fill free to open Issues & report bugs. I will solve them as soon as possible.

Problem Context
---------------

On my current project I works a lot with AWS Lambdas & tries to up & run them with SAM local. 
And there is some issues especially when you work on the project with a big count of lambdas.

Some of them:

1) First of all it does not allow skip some lambdas form config
2) It build lambdas inside each docker container so it takes significant time to build/rebuild & up all containers (and you need up all containers if you want to have fast integration tests)

Both points in the mix make impossible to use SAM in weak developers envs like VDI, for example.

Changelog
---------

**v0.3.0**


#. Added Possimility to run multiple workers with flag --workers. 
   This helpful if you need speed up your local server or some lambdas need to call another lambdas directly.
#. Added flag --reload to cli if you want auto reload server when code changed (uvicor --reload)
#. Added support for Cloud Formation templates in JSON

**v0.2.3**


#. Possibility to send port & host to start several instances in same time.

**v0.2.2**


#. README.md is updated
#. Fixed Issue with lambdas in template, that does not have Events with Path (like S3 triggered lambdas)
#. Fixed issue with status code 204 - now it returns correct answer with no failes.
#. Added some tests

**v0.2.1**


#. Now LoF do not try/except lambdas errors

**v0.2.0**


#. Fixed status_code resend from lambda & JSON body response

**v0.1.0**


#. First version of Lambdas on FastApi. 
   Based on AWS CloudFormation template it's serve lambdas as FastAPI endpoints for local testing.
