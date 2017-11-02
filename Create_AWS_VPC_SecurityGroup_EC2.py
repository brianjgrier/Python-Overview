#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This is not really a script, which is why there is no extension to the file.
# This is a collection of commands I am testing to determine what I want as
# functions and variables in the actual script.
#
# I will upate this and then cut/paste commands from here into an
# interactive python session to test how it works.
#
import sys
import json

import boto3
import logging

import pprint
from pprint import pprint as pp

import mysql.connector
from mysql.connector import errorcode

import db


#pp = pprint.PrettyPrinter(indent=4)

def listVPCs(ec2):
    for a in ec2.vpcs.all():
        print
        if a.tags != None:
            for b in a.tags:
                print b['Key'] + ": " + b['Value']
        for b in a.route_tables.all():
            pp(b.id)

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))
            

class global_stuff:
   myId         = 'Not Defined'
   owner        = None
   ec2          = None
   ec2c         = None
   group        = None
   resourceBase = None
   fqdnBase     = None
   idSeparator  = None
   custId       = 'Not Defined'
   awsAbbrv     = None
   regionIdx    = None
   regionList   = None
   serverList   = None
   DBsubnets    = None
   DBsecurity   = None
   aZone        = None
   vpc          = None
   routeTable   = None
   subnets      = []
   security     = None
   gateway      = None
   Nats         = None
   instances    = None
   jumpExtIP  = None
   resText      = ""

#
# Record any issues.
# Originally this went to a file, now it is stacked up and stored in the
# table "orchestration_journal" in the "reason" field
#
def resCapture(what, problem):
    print "Filling in the error"
    P.resText += "Encountered error while {}\r\n".format(what)
    P.resText += "    Error - {} - {}\r\n".format(sys.exc_info()[0], sys.exc_info()[1])
    P.resText += "          - {}\r\n".format(type(problem))
#    P.resText += "          - {}\r\n".format(problem.args)
#    P.resText += "          - {}\r\n".format(problem)
    P.resText += "\r\n"
    print(P.resText)


#
# This is a basic prompt and get response function with a twist...
# The function takes one of two arugments, it will reject both
#
# 1) Prompt="xxx" - returns a string
# 2) List = ['First string', 'Second String', ...'nth String'] - returns index
#
def getUserInput(**kwargs):
    result = None
    if kwargs is not None:
        if 'Prompt' in kwargs.keys():
            if 'List' not in kwargs.keys():
                result = raw_input(kwargs['Prompt'])
        else:
            if 'List' in kwargs.keys():
                inputNotValid = True
                while inputNotValid:
                    cntr = 0
                    for x in kwargs['List']:
                        cntr = cntr + 1
                        print "%s) %s"%(cntr, x)
                    result = raw_input("Enter Selection: ")
                    try:
                        it = int(result)
                        if it > 0 and it <= cntr:
                            inputNotValid = False
                    except ValueError:
                        inputNotValid = True
                    print 'Please enter an integer in the range 1 to %s'%(cntr)
    return result
            

def checkTagSet(resource, tagKey, tagValue):
    result = False
    for a in resource.all():
        if a.tags != None:
            for b in a.tags:
                if tagKey == b['Key']:
                    if tagValue == b['Value']:
                        result = True
                        break;
    return result

def setTags(ResId, resName):
    P.ec2.create_tags(DryRun=False,
                           Resources=[ResId],
                           Tags=[{
                                     'Key': 'Name',
                                     'Value': resName
                                 },
                                 {
                                     'Key': 'Customer',
                                     'Value': P.custId
                                 },
                                 {
                                     'Key': 'Data Classification',
                                     'Value': 'Company Confidential'
                                 },
                                 {
                                     'Key': 'Environment',
                                     'Value': 'NonProd'
                                 },
                                 {
                                     'Key': 'Resource Owner',
                                     'Value': P.owner
                                 },
                                 {
                                     'Key': 'Application Name',
                                     'Value': 'XYZ - Your Application name here'
                                 },
                                 {
                                     'Key': 'Mail Alias',
                                     'Value': 'xyz-adm'
                                 },
                                 {
                                     'Key': 'Security Compliance',
                                     'Value': 'Yes'
                                 },
                                ])


def main():
    result = 0

    P.custId = getUserInput(Prompt="Customer Id: ")


    P.owner        = db.queryKeyPairs('Owner')
    P.group        = db.queryKeyPairs('Groupname')
    ResSeparator   = db.queryKeyPairs('ResourceIdSeparator')
    Separator      = db.queryKeyPairs('FQDNseparator')

#
# These input options should be pulled from table "regions"
#
    P.regionList = db.loadRegionTable()
    abbrvList = []
    for x in P.regionList:
        abbrvList.append(x['descr'])
        
    regionIdx = int(getUserInput(List=abbrvList)) -1
    
#    P.region = P.regionList[regionIdx]['AWSRegion']
    P.awsAbbrv = P.regionList[regionIdx]['abbrv']

    P.resourceBase = ''.join([P.group, ResSeparator, P.custId])
    P.fqdnBase     = ''.join([Separator, P.custId, Separator, P.awsAbbrv])
    regionInfo = P.regionList[regionIdx]['AWSRegion']
    cidrInfo = P.regionList[regionIdx]['CIDR']

#
# This results in tow name formats. The first is the human readable
# right to left format of the AWS resources:
#
#   alm-cliqr...
#   alm-openvpn...
#
# It has also produced the base of the fqdn simulation we will be using
#
#   .cliqr.ore
#   .opendns.ore
#
    print P.resourceBase + '  -  ' + P.fqdnBase

#
# take care of a few general items.
# First is get the account id for your AWS account. You can find it
# via the web access under your account information.
#
    P.myId = boto3.client('sts').get_caller_identity()['Account']
#
# Even though the script allows you to specify a region/data center
# the script initially only pulls the regon from your aws configuration
# that was set up when you use the awscli to configure your access.
#
#
    P.ec2c = boto3.client('ec2', region_name=regionInfo)
    r = P.ec2c.describe_availability_zones()
    azs = r.get('AvailabilityZones')
    az_list = [az.get('ZoneName') for az in azs if az.get('State') == 'available']
    P.aZone = az_list[0]
#
# Now get ready to create resources
#
    P.ec2 = boto3.resource('ec2', region_name=regionInfo)
#
# First thing to do is to make sure the customer is not already set up in this region
#
    if checkTagSet(P.ec2.vpcs, 'Customer', P.custId)== True:
        print "Customer: %s already exists"%(P.custId)
        print "Exiting..."
        P.resText += "Customer: %s already exists"%(P.custId)
        result = -1
    else:
        print("Getting Resources from AWS")
        sys.stdout.flush()

        P.serverList = db.getServerInfo()
#
# Now that we have the server info from the database let the user change the default size for storage.
# Because I am lazy, and I don't want a confusing mess for the user, only allow one size for secondary
# storage. Because only the DB server will should have it, and they all have to be the same anyways.
#
# BAD CODING ALERT!!!
# in P.serverList the servernames are what is used in the DB. If those names change this code breaks!!
# VERY BAD DESIGN NEED TO RETHINK THIS!!!
#
        serverSize = {}
        serverSize['Jira'] = P.serverList['jira']['mainStorage']
        serverSize['Conflence'] = P.serverList['conf']['mainStorage']
        serverSize['Database'] = P.serverList['pgres1']['extraStorage']
        response = ''
        while response == '':
            print
            print "Preconfigured Storage:"
            for a in serverSize.keys():
                print "%s - %sGiB"%(a, serverSize[a])
            print "Would you like to change any of these values?"
            response = getUserInput(Prompt="Y/y = Yes; ")
        
        if response in 'Yy':
            badValue = True
            while badValue:
                storage = 1
                try:
                    storage = int(getUserInput(Prompt="Storage for Jira: "))
                    badValue = False
                except ValueError:
                    print 'you must enter a number, try again'
                P.serverList['jira']['mainStorage'] = storage
                
            badValue = True
            while badValue:
                storage = 1
                try:
                    storage = int(getUserInput(Prompt="Storage for Confluence: "))
                    badValue = False
                except ValueError:
                    print 'you must enter a number, try again'
                P.serverList['conf']['mainStorage'] = storage

            badValue = True
            while badValue:
                storage = 1
                try:
                    storage = int(getUserInput(Prompt="Storage for the database: "))
                    badValue = False
                except ValueError:                    print 'you must enter a number, try again'
                P.serverList['pgres1']['extraStorage'] = storage
                P.serverList['pgres2']['extraStorage'] = storage
                P.serverList['pgpool']['extraStorage'] = storage

#        pp(P.serverList)
#        return result
#
# Only allow AMIs that we have created.
#
        for a in P.ec2.images.filter(DryRun=False, Owners=[P.myId]):
            for b in P.serverList.keys():
                if a.name == P.serverList[b]['AMI']:
                    P.serverList[b]['AMI_Id'] = a.image_id
                    P.serverList[b]['Disks'] = []
#
# We have it all, but actually we have more than the rest API will accept in the
# device mapping field. We will have to remove the "Encrypted" field from the
# "Ebs" dictionaries. There is a way to delete an entry from a dictionary, but I am
# brain dead right now so...
#
                    devCtr = 0
                    for devBlk in a.block_device_mappings:
#                        pp(devBlk)
                        P.serverList[b]['Disks'].append({})
                        P.serverList[b]['Disks'][devCtr]['DeviceName'] = devBlk['DeviceName']
                        P.serverList[b]['Disks'][devCtr]['Ebs'] = {}
                        P.serverList[b]['Disks'][devCtr]['Ebs']['DeleteOnTermination'] = True
                        P.serverList[b]['Disks'][devCtr]['Ebs']['SnapshotId'] = devBlk['Ebs']['SnapshotId']
#
# If the DB wants a larger drive primary drive than the AMI allow it.
# Do not allow a smaller drive, there may be a reason it is as big as it is.
#
                        if devCtr == 0:
                            if P.serverList[b]['mainStorage'] > devBlk['Ebs']['VolumeSize']:
                                P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeSize'] = P.serverList[b]['mainStorage']
                            else:
                                P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeSize'] = devBlk['Ebs']['VolumeSize']
                        elif devCtr == 1:
                            if P.serverList[b]['extraStorage'] > devBlk['Ebs']['VolumeSize']:
                                P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeSize'] = P.serverList[b]['extraStorage']
                            else:
                                P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeSize'] = devBlk['Ebs']['VolumeSize']
                        
                        P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeType'] = devBlk['Ebs']['VolumeType']
                        devCtr = devCtr + 1

#
# now the original image may not have specified extra storage so...
# check if the server is requesting it and it was not in the AMI.
# If that is true add it to the list of devices, as /dev/sdb
#
                    if devCtr == 1:
                        if P.serverList[b]['extraStorage'] > 0:
                            P.serverList[b]['Disks'].append({})
                            P.serverList[b]['Disks'][devCtr]['DeviceName'] = '/dev/sdb'
                            P.serverList[b]['Disks'][devCtr]['Ebs'] = {}
                            P.serverList[b]['Disks'][devCtr]['Ebs']['DeleteOnTermination'] = True
                            P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeSize'] = P.serverList[b]['extraStorage']
                            P.serverList[b]['Disks'][devCtr]['Ebs']['VolumeType'] = 'gp2'

        oops = False
        for b in P.serverList.keys():
            if P.serverList[b]['AMI_Id'] == None:
                if oops == False:
                    P.resText += "Cannot create at least one server, invalid AMI specified"
#                    print "Cannot create at least one server, invalid AMI specified"
                    oops = True
                p.resText += "   Region %s - AMI not available: %s"%(regionIdx, P.serverList[b]['AMI'])
#                print "   Region %s - AMI not available: %s"%(regionIdx, P.serverList[b]['AMI'])

#        pp(P.serverList)
#        sys.stdout.flush()

        if oops == True:
            result = -1
            return result
#
# Get the CIDR for the vpc
#
        P.DBsubnets = db.getSubnetInfo()
#        print len(P.DBsubnets)
#        pp(P.DBsubnets)
        P.DBsecurity = db.getSecurityInfo(P.custId, P.myId)
#        pp(P.DBsecurity)

#        return result
#
# We have the security info, BUT...
# Because security groups reference eachother by security group id
# this table is not quite complete. It cannot be complete until we
# have the security group ids. So we need to create them BUT...
#
# But before we can do that we need the VPC in existance because
# security groups are associated with a single vpc...
#
#        print "Creating VPC for %s"%(P.custId)
        P.resText += "Creating VPC for %s"%(P.custId)
        sys.stdout.flush()

        try:
            P.vpc = P.ec2.create_vpc(CidrBlock=cidrInfo)
        except Exception as exc:
            print "OOOPs!!! there is an error!!!"
            resCapture("Creating VPC Resource: {}".format(P.resourceBase), exc)
            result = -1
            return result

        setTags(P.vpc.id, P.resourceBase)

        print "    Creating Security Groups"
        P.resText += "    Creating Security Groups"
        sys.stdout.flush()
        
        counter = 0
        for groupname in P.DBsecurity.keys():
            sg = P.vpc.create_security_group(DryRun = False,
                                             GroupName = groupname,
                                             Description = "Security group for %s"%(groupname))
            setTags(sg.id, ''.join([P.resourceBase, ResSeparator, groupname]))
            P.DBsecurity[groupname]['resource'] = sg

#
# We currently have an ALMOST complete security group profile.
# what is missing is the Amazon Resource IDs are not filled into the
# "GroupId" of thIdGroupPairs" Loop through every entry and fill in the
# value saved in the "resource" key
#
        for groupname in P.DBsecurity.keys():
            counter = 0
            inLength = len(P.DBsecurity[groupname]['Inbound'])
            while counter < inLength:
                sgGroups = P.DBsecurity[groupname]['Inbound'][counter]['UserIdGroupPairs']
                numGroups = len(sgGroups)
                if numGroups > 0:
                    innerCtr = 0
                    while innerCtr < numGroups:
                        refGroup = sgGroups[innerCtr]['GroupId']
                        P.DBsecurity[groupname]['Inbound'][counter]['UserIdGroupPairs'][innerCtr]['GroupId'] = P.DBsecurity[refGroup]['resource'].id
                        innerCtr = innerCtr + 1

                sg = P.DBsecurity[groupname]['resource']
#                print counter
                counter = counter + 1

#            pp(P.DBsecurity[groupname])
            sg.authorize_ingress(DryRun = False,
                                 IpPermissions = P.DBsecurity[groupname]['Inbound'])
#
# We are not yet dealing with egress rules, though you can put them in the database
# so just let everything out until I have time to handle this. (this is the default)
#
                                
#
# Create and attach a Gateway
#
        print "    Creating gateway"
        P.resText += "    Creating gateway"
        P.gateway = P.ec2.create_internet_gateway()
        P.gateway.attach_to_vpc(VpcId=P.vpc.id)
        setTags(P.gateway.id, P.resourceBase)
#
# The previous command did not just create a vpc it also created
# a route table, which is not what the documentation says it will do.
# The documentation implies that the route table would still need to
# be created. We need to get the ID of that route table so we can apply
# the tags to it, and so that we can associate the subnets to it.
#
# Normally something that is iterable has an iterator attached to it.
# Such is not the cae for resources returned by Boto3...
# Since there is only one route table at this point this cheat will work
#
        for b in P.vpc.route_tables.all():
            P.routeTable = P.ec2.RouteTable(b.id)
#
# Here we need to create a route and associate it with the internet gateway
#
        P.routeTable.create_route(DryRun=False,
                                  DestinationCidrBlock='0.0.0.0/0',
                                  GatewayId=P.gateway.id)                                      
            
        setTags(P.routeTable.id, P.resourceBase)
        for snet in P.DBsubnets:
            tSnet = P.ec2.create_subnet(DryRun=False,
                                        VpcId=P.vpc.id,
                                        CidrBlock=P.DBsubnets[snet]['CIDR'],
                                        AvailabilityZone=P.aZone)
            P.DBsubnets[snet]['sNet_Id'] = tSnet.id
            P.routeTable.associate_with_subnet(DryRun=False,
                                               SubnetId=tSnet.id)
            setTags(tSnet.id, ''.join([P.resourceBase, ResSeparator, P.DBsubnets[snet]['Name']]))
            P.subnets.append(tSnet)

#        pp(P.DBsubnets)
        pp(P.subnets)

#        return

        print "    Creating VMs"
        P.resText += "    Creating VMs"

#
# Need to get security key id...
# but right now who cares... I am just going to delete these for quite a while
#
        try:
            for a in P.serverList.keys():
#                print "Starting server: %s image - %s"%(a, P.serverList[a]['AMI_Id'])
                if P.serverList[a]['AMI_Id'] != None:
#                    print "   subnet: %s"%(P.serverList[a]['subnet'])
                    sNetId = P.DBsubnets[P.serverList[a]['subnet']]['sNet_Id']
                    pubAddr = False
                    if P.DBsubnets[P.serverList[a]['subnet']]['pubPriv'] == 1:
                        pubAddr = True
                    print "        Standing up server %s in subnet %s"%(a, sNetId)
                    P.resText += "        Standing up server %s in subnet %s"%(a, sNetId)
                    for b in P.subnets:
                        if b.id == sNetId:
                            sgId = P.DBsecurity[P.serverList[a]['securityGroup']]['resource'].id
                            localIp = P.serverList[a]['localIp']
                            vm = P.ec2.create_instances(DryRun=False,
                                                        ImageId  = P.serverList[a]['AMI_Id'],
                                                        MinCount = 1,
                                                        MaxCount = 1,
                                                        KeyName  = P.serverList[a]['securityKey'],
                                                        InstanceType = P.serverList[a]['InstType'],
                                                        DisableApiTermination = True,
                                                        InstanceInitiatedShutdownBehavior='stop',
                                                        NetworkInterfaces = [{
                                                                                'DeviceIndex' : 0,
                                                                                'SubnetId'    : sNetId,
                                                                                'Groups'      : [sgId],
                                                                                'PrivateIpAddress': P.serverList[a]['localIp'],
                                                                                'AssociatePublicIpAddress': pubAddr
                                                                            }],
                                                        BlockDeviceMappings = P.serverList[a]['Disks']
                                                        )
#
# Since we are only standing up one at a time, only
# one instance will get its tags set
#
# Did I ever mention that while I really like the Python's flexibility
# I REALLY HATE having to keep track in indentation... Just sayin
#
                            for instance in vm:
                                setTags(instance.id, ''.join([P.resourceBase, ResSeparator, a]))
                                instance.wait_until_running(DryRun=False,
                                                                Filters = [
                                                                    {
                                                                        'Name' : 'instance-id',
                                                                        'Values' : [instance.id,]
                                                                        },
                                                                    ])
#
# Now that the instance is running get all the information again.
# This will populate the external IP address if it was requested.
#
                                instance.reload()
                                if a == 'jump':
                                    P.jumpExtIP = instance.public_ip_address

                                
                                setTags(instance.id, ''.join([P.resourceBase, ResSeparator, a]))

#
#
            print
            print "Add the following lines to the file /etc/ssh/ssh_config"
            print
            print "Host %s"%(''.join(["*", P.fqdnBase]))
            print "        ForwardAgent yes"
            print "        User ec2-user"
            print "        ProxyCommand ssh \%r\@{} nc \%h \%p -w 10".format(P.jumpExtIP)
            print
            print

            print
            print "Use the following lines to replace the /etc/hosts file on the jump server"
            print
            print "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4"
            print "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6"
            print
            for a in P.serverList.keys():
                if a != 'jump':
                    print "%s   %s"%(P.serverList[a]['localIp'], ''.join([a, P.fqdnBase]))
            print

#
# Just found out there is a network resource created when an instance
# is created. Currently it has no tags so you can not see what is attached to what.
# Not going to handle this now, but it should be done at some point in time
# for completeness reasons
#
        except Exception as exc:
            print "OOOPs!!! there is an error!!!"
            resCapture("Creating EC2 instances: {}".format(''.join([P.resourceBase, ResSeparator, a])), exc)
            result = -1

        

    return result


#
# using this to prevent the file from running if someone decides
# to "import" this into their program
#
P = global_stuff()

logging.getLogger('botocore').setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.DEBUG)

if __name__ == "__main__":
    result = -1
    if db.dbOpen() == True:
        result = 0
        if len(sys.argv) > 1:
            print "No arguments are supported by this application!"
        else:
            result = main()
            db.createOrchJournalEntry(P.custId, result, P.resText)
            db.dbClose()
    
    sys.exit(result)
