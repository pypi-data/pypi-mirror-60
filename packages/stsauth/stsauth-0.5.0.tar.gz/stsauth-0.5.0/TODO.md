https://stackoverflow.com/questions/52706049/how-to-test-a-python-cli-program-with-click-coverage-py-and-tox

Support finding aws config file pattern (https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

- use ~/.aws/config
- use ~/.aws/credentials
- use AWS_CONFIG_FILE environment variable

```sh
$ stsauth authenticate -u s103151 -p $(pass bbva) -s $(pass bbva-ss) -l $AWS_PROFILE


Requesting credentials for role: arn:aws:iam::267204760080:role/ADFS-PLAY-TOOLS-DevOpsEngineer
Traceback (most recent call last):
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/sts_auth/stsauth.py", line 230, in fetch_aws_sts_token
    sts = boto3.client('sts')
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/boto3/__init__.py", line 91, in client
    return _get_default_session().client(*args, **kwargs)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/boto3/__init__.py", line 80, in _get_default_session
    setup_default_session()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/boto3/__init__.py", line 34, in setup_default_session
    DEFAULT_SESSION = Session(**kwargs)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/boto3/session.py", line 80, in __init__
    self._setup_loader()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/boto3/session.py", line 120, in _setup_loader
    self._loader = self._session.get_component('data_loader')
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/session.py", line 679, in get_component
    return self._components.get_component(name)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/session.py", line 902, in get_component
    self._components[name] = factory()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/session.py", line 150, in <lambda>
    lambda:  create_loader(self.get_config_variable('data_path')))
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/session.py", line 233, in get_config_variable
    logical_name)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/configprovider.py", line 226, in get_config_variable
    return provider.provide()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/configprovider.py", line 323, in provide
    value = provider.provide()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/configprovider.py", line 382, in provide
    config = self._session.get_scoped_config()
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/botocore/session.py", line 334, in get_scoped_config
    raise ProfileNotFound(profile=profile_name)
botocore.exceptions.ProfileNotFound: The config profile (267204760080-ADFS-PLAY-TOOLS-DevOpsEngineer) could not be found

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/s103151/.pyenv/versions/3.6.5/bin/stsauth", line 10, in <module>
    sys.exit(cli())
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/click/core.py", line 764, in __call__
    return self.main(*args, **kwargs)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/click/core.py", line 717, in main
    rv = self.invoke(ctx)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/click/core.py", line 1137, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/click/core.py", line 956, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/click/core.py", line 555, in invoke
    return callback(*args, **kwargs)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/sts_auth/cli.py", line 117, in authenticate
    token = sts_auth.fetch_aws_sts_token(role_arn, principal_arn, saml_response.assertion)
  File "/Users/s103151/.pyenv/versions/3.6.5/lib/python3.6/site-packages/sts_auth/stsauth.py", line 232, in fetch_aws_sts_token
    click.secho(e.response['Error']['Message'], fg='red')
AttributeError: 'ProfileNotFound' object has no attribute 'response'
```
