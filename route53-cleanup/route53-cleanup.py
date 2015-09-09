#!/usr/bin/env python
# Based on https://github.com/fsalum/scripts/tree/master/Route53Cleanup, but
# use zone name instead of zone id.
import sys
import argparse
import re
import boto.ec2
from boto.ec2 import regions
from boto.route53.connection import Route53Connection
from boto.route53.exception import DNSServerError
from collections import defaultdict

description = 'Route53 Cleanup Reporter'
version = '%(prog)s 0.1'
usage = '%(prog)s --zonename domain.tld.'

def options():
    parser = argparse.ArgumentParser(usage=usage,description=description)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-r', '--region', dest='region', default='eu-west-1', required=False, action='store', nargs='?', help='EC2 Region (Defaults: eu-west-1)')
    group = parser.add_argument_group('required arguments')
    group.add_argument('-z', '--zonename', dest='zonename', default='None', required=True, action='store', nargs='?', help='Hosted Zone Name')
    args = parser.parse_args()
    return args

def get_ec2(args):
    ec2_ips = defaultdict(dict)

    # Connect the region
    for r in regions():
        if r.name == args.region:
            region = r
            break
    else:
        print "Region %s not found." % args.region
        sys.exit(1)

    print "Retrieving EC2 records..."
    conn = boto.connect_ec2(region=region)
    reservations = conn.get_all_reservations()

    for reservation in reservations:
        instances = reservation.instances
        for instance in instances:
            if instance.state == 'running': # or instance.state == 'stopped':
                ec2_ips[instance.id]['private_ip'] = instance.private_ip_address
                ec2_ips[instance.id]['public_ip'] = instance.ip_address
                ec2_ips[instance.id]['private_dns'] = instance.private_dns_name
                ec2_ips[instance.id]['public_dns'] = instance.public_dns_name

    return ec2_ips

def get_route53(args):
    route53_ips = {}
    conn = Route53Connection()

    # Get all hosted zones
    try:
        results = conn.get_all_hosted_zones()
    except e:
        print "ERROR %s" % e

    # Make sure zonename ends with a dot
    if args.zonename[-1:] != '.':
        args.zonename += "."

    # Find zone
    zone_id = ""
    for zone in results['ListHostedZonesResponse']['HostedZones']:
        if zone['Name'] == args.zonename:
            zone_id = zone['Id'].replace('/hostedzone/', '')

    if zone_id == "":
        print "Zonename %s not found." % args.zonename
        sys.exit(1)

    print "Retrieving Route53 records..."
    records = conn.get_all_rrsets(zone_id)

    for record in records:
        if record.type == 'A':
            route53_ips[record.name] = record.resource_records[0]
        elif (record.type == 'CNAME'
            and (record.resource_records[0].endswith('.compute.amazonaws.com')
                or record.resource_records[0].endswith('.internal'))):
            route53_ips[record.name] = record.resource_records[0]

    return route53_ips

def main():
    args = options()
    route53_ips = get_route53(args)
    ec2_ips = get_ec2(args)
    report_ips = {}

    # Lookup Route53 IP on EC2
    for name,ip in route53_ips.items():
        match = 0
        for ec2_id in ec2_ips:
            if ip in ec2_ips[ec2_id].values():
                match = 1
        if match == 0:
            report_ips[name] = ip

    for name,ip in sorted(report_ips.items()):
        if re.match('[\d\.]+', ip):
            print "A;%s;%s" % (ip,name)
        else:
            print "CNAME;%s;%s" % (ip,name)

if __name__ == '__main__':
    main()
