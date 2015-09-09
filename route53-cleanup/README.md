Route53Cleanup
--------------

Report on Route53 IP records not found in the EC2 running and stopped instances.

```
usage: route53-cleanup.py --zonename domain.tld.

Route53 Cleanup Reporter

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -r [REGION], --region [REGION]
                        EC2 Region (Defaults: eu-west-1)

required arguments:
  -z [ZONENAME], --zonename [ZONENAME]
                        Hosted Zone Name
```
