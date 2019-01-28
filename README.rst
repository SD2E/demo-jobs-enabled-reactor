=========================================
Reactor+App with PipelineJobs Integration
=========================================

This is an example implementation of a Reactor that launches an Agave app,
where both Reactor and the App integrate with the PipelineJobs system to
update the state and history of a PipelineJob.

Key Aspects
-----------

Note the following as you go through the code and configuration of this project:

#. Use of the ``ManagedPipelineJob`` class to instantiate the job
#. Addition of Agave job notifications allowing the job to send updates
#. Configuration of this Reactor via the ``mongodb`` and ``pipelines`` stanzas in ``config.yml``
#. Use of Abaco API keys, or _nonces_, in ``secrets.json``
#. Leveraging shared Abaco Reactors


Deploying your own Reactor
--------------------------

.. note:: Familiarity with configuration and deployment of Abaco Reactor is assumed.

Obtain the following values from the Infrastructure team for *secrets.json*:

* ``_REACTOR_MONGODB_AUTHN``
* ``_REACTOR_PIPELINES_JOB_MANAGER_NONCE``

Confirm the following values with the Infrastructure team for *config.yml*:

* ``pipelines.job_manager_id``
* ``pipelines.job_indexer_id``

.. danger:: Never include values from **secrets.json** in ``config.yml`` file.
   If you do this, they will be committed forever to a publicly-accessible
   Docker image when the Reactor is deployed.

Once you've set up the configuration and secrets, build then deploy your Reactor.

Send a Message
--------------

.. code-block:: console

    abaco run -m '{"data":{"key1":"value 1"}, "sample_id": "sample.tacc.20001}' <ACTOR_ID>

