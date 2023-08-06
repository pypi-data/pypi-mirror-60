# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_assume']

package_data = \
{'': ['*']}

install_requires = \
['aws_credential_process>=0.1.0,<0.2.0', 'click==7.0']

entry_points = \
{'console_scripts': ['_assume = aws_assume._assume:main']}

setup_kwargs = {
    'name': 'aws-assume',
    'version': '0.2.2',
    'description': 'AWS session token refreshing daemon',
    'long_description': "AWS Assume daemon\n=================\n\nThis script automatically assumes every 15 minutes the specified role using a\nYubikey as MFA (multi factor authentication) and updates `~/.aws/credentials`.\n\nAs long as you've got your yubikey connected to your computer you'll never\nhave to enter a second factor authentication code for the aws cli. As other\ntools / libraries (boto3) use `~/.aws/credentials` as well you don't have to\nenter a token for these either.\n\nUsage\n=====\n\nYou can install aws_assume using pip (`pip install aws_assume`), I recommend\nto install aws_assume using poetry (`poetry install aws_assume`) or in a\nvirtualenv.\n\nYour `~/.aws/credentials` should contain your credentials and a profile with\nthe the keys `aws_access_key_id`, `aws_secret_access_key` and\n`aws_session_token`.\n\nFor example:\n\n`~/.aws/credentials`\n\n```ini\n[default]\naws_access_key_id = ...(your key id)...\naws_secret_access_key = ...(your access key)...\n\n[profile]\naws_access_key_id = ...(placeholder, can be anything)...\naws_secret_access_key = ...(placeholder, can be anything)...\naws_session_token = ...(placeholder, can be anything)...\n```\n\nYour `~/.aws/credentials` will be updated in place, only the specified profile\nsection should be touched (your comments will be safe).\n\nOlder versions are rotated up to 5 items.\n\nNext `_assume` should be started with the following arguments:\n\n```bash\n_assume --rolearn ... --oath_slot=... --serialnumber=... --profile_name=... --access-key-id=... --secret-access-key=... --mfa-session-duration=...\n```\n\nArgument                 | Description\n-------------------------|-------------------------------------\n`--rolearn`              | arn of the role you'd like to assume\n`--oath_slot`            | oath slot on your yubikey\n`--serialnumber`         | serial number of your MFA\n`--profile_name`         | profile used in `~/.aws/credentials`\n`--access-key-id`        | access key (as obtained from IAM console)\n`--secret-access-key`    | secret access key (as obtained from IAM console)\n`--mfa-session-duration` | duration (in seconds) for MFA session\n`--credentials-section`  | you can specify a different section than default in `~/.aws/credentials`\n\nYou should only run one `_assume` process per profile, I use systemd for\nstarting `_assume`, by using the following unit file:\n\n`~/.config/systemd/user/aws_assume@.service`\n\n```ini\n[Unit]\nDescription=Amazon Web Services token daemon\n\n[Service]\nType=simple\nExecStart=%h/bin/_assume --rolearn='...%i...' --oath_slot=... --serialnumber=... --profile_name='...%i...' --access-key-id='...' --secret-access-key='...'\nRestart=on-failure\n\n[Install]\nWantedBy=default.target\n```\n\nAnd reload systemd using `systemctl --user daemon-reload`, start `_assume` using\n`systemctl --user start aws_assume@...`\n\nIf you're not so fortunate to have systemd you can also use something like\n`supervisord` to start `_assume`.\n\n`~/supervisord.conf`\n\n```ini\n[supervisord]\n\n[supervisorctl]\nserverurl=unix:///home/user/supervisord.sock\n\n[unix_http_server]\nfile=/home/user/supervisord.sock\n\n[rpcinterface:supervisor]\nsupervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\n[program:assume-...]\ncommand=/home/user/bin/_assume --rolearn=... --oath_slot=... --serialnumber=... --profile_name=... --access-key-id=... --secret-access-key=...\nautorestart=true\n```\n\nStart supervisord using `supervisord -c supervisor.conf` and start assume using\n`supervisorctl -c supervisor.conf start assume-...`.\n",
    'author': 'Dick Marinus',
    'author_email': 'dick@mrns.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/meeuw/aws_assume',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
