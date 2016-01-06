#!/usr/bin/env python

import boto
import boto.ec2
import boto.ec2.elb
import boto.rds
import pprint
import argparse

def lookup_by_id(sgid):
    sg = ec2.get_all_security_groups(group_ids=sgid)
    return sg[0].name

# Set credentials below, unless you want them to come from the environment
#ACCESS_KEY=""
#SECRET_KEY=""

#get a full list of the available regions
region_list=[]
counter=0
regions = boto.ec2.regions()
for i in regions:
	#print regions[counter].name
	region_list.append(str(regions[counter].name))
	counter=counter+1

parser = argparse.ArgumentParser(description="Show unused security groups")
parser.add_argument("-r", "--region", type=str, default="us-east-1", help="The default region is us-east-1. The list of available regions are as follows: %s" % sorted(region_list))
parser.add_argument("-d", "--delete", help="delete security groups from AWS")
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)

ec2 = boto.ec2.connect_to_region(args.region)

allgroups = []
# Get ALL security groups names
groups = ec2.get_all_security_groups()
for groupobj in groups:
    allgroups.append(groupobj.name)

# Get all instances security groups
groups_in_use = ['default']
reservations = ec2.get_all_instances()
for r in reservations:
	for ec2_group_list in r.groups:
		if ec2_group_list.name not in groups_in_use:
			groups_in_use.append(ec2_group_list.name)

elb = boto.ec2.elb.connect_to_region(args.region)
load_balancers = elb.get_all_load_balancers()
for load_balancer in load_balancers:
    if load_balancer.source_security_group.name not in groups_in_use:
        groups_in_use.append(load_balancer.source_security_group.name)

rds = boto.rds.connect_to_region(args.region)
dbs = rds.get_all_dbinstances()
for db in dbs:
    if len(db.vpc_security_groups) > 0:
        sg_name = lookup_by_id(db.vpc_security_groups[0].vpc_group)
        if sg_name not in groups_in_use:
            groups_in_use.append(sg_name)

enis = ec2.get_all_network_interfaces()
for eni in enis:
    for eni_grp in eni.groups:
      if eni_grp.name not in groups_in_use:
        groups_in_use.append(eni_grp.name)

delete_candidates = []
for group in allgroups:
    if group not in groups_in_use and not group.startswith('AWS-OpsWorks-'):
        delete_candidates.append(group)

if args.delete:
    print "We will now delete security groups identified to not be in use."
    for group in delete_candidates:
        ec2.delete_security_group(group)
else:
    print "The list of security groups to be removed is below."
    print "Run this again with `-d` to remove them"
    #pp.pprint(sorted(delete_candidates))
    for group in sorted(delete_candidates):
        print "   " + group

print "---------------"
print "Activity Report"
print "---------------"

print "Total number of Security Groups evaluated: %d" % (len(groups_in_use))
print "Total number of EC2 Instances evaluated: %d" % (len(reservations))
print "Total number of Load Balancers evaluated: %d" % (len(load_balancers))
print "Total number of RDS instances evaluated: %d" % (len(dbs))
print "Total number of Network Interfaces evaluated: %d" % (len(enis))
if args.delete:
	print "Total number of security groups deleted: %d" % (len(delete_candidates))
else:
	print "Total number of security groups targeted for removal: %d" % (len(delete_candidates))
