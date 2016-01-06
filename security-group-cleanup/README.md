security-group-cleanup
--------------

Script reads AWS credentials from the environment, unless you define `ACCESS_KEY` and `SECRET_KEY` inside the script.

```
usage: security-group-cleanup.py [-h] [-r REGION] [-d DELETE]

Show unused security groups

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        The default region is us-east-1. The list of available
                        regions are as follows: ['ap-northeast-1', 'ap-
                        southeast-1', 'ap-southeast-2', 'cn-north-1', 'eu-
                        central-1', 'eu-west-1', 'sa-east-1', 'us-east-1',
                        'us-gov-west-1', 'us-west-1', 'us-west-2']
  -d DELETE, --delete DELETE
                        delete security groups from AWS
```
