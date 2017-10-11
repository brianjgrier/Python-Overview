import sys
import json
import datetime
import time

import boto3

import pprint
from pprint import pprint as pp

import mysql.connector
from mysql.connector import errorcode

vpctemplateAccess = {
  'user': 'play',
  'password': 'Mine',
  'host': '127.0.0.1',
  'database': 'engit-aws-vpc-templates',
  'raise_on_warnings': True,
}

vpcAccess = {
  'user': 'aws_creator',
  'password': 'theusual',
  'host': '127.0.0.1',
  'database': 'engit-aws',
  'raise_on_warnings': True,
}



cnx = None


def dbOpen():
    result = False
    try:
        global cnx
        cnx = mysql.connector.connect(**vpctemplateAccess)
        result = True
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    
    return result

def dbClose():
    cnx.close()


def createOrchJournalEntry(customer, result, resultText):
    if result == 0:
        orchStatus = "Created"
    else:
        orchStatus = "Error"

    c = cnx.cursor()
    u = "INSERT INTO orchestration_journal (custId, Result, Reason, Time_Stamp)"
    u += " VALUES(%s, %s, %s, %s)"
    c.execute(u, (customer, orchStatus, resultText, datetime.datetime.now()))

    cnx.commit()

    return

def getAddressTable():
    query = ("SELECT * FROM AddressTable")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, ())
    AT_rows = vpcCursor.fetchall()
    ATs = {}
    for (var1, var2) in AT_rows:
        if var1.encode() not in ATs:
            ATs[var1] = []
        x = var2.encode()
        temp = {}
        temp['CidrIp'] = x
        ATs[var1].append({'CidrIp': var2})
    return ATs


def getSecurityInfo(vpcId, AWSuserId):
#
# to do this we informtionfrom two tables. Those tables are "security_rules" and "AddressTable"
# 
    result = {}
    placeHolder = " "
    productionValue = "0"
    query = ("SELECT * FROM security_rules")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, ())
    sg_rows = vpcCursor.fetchall()
#
# Now get the information from the "AddressTable"
#
    ipAddrs = getAddressTable()
#
# Start building the security group matrix
#
    sgs = {}
    for (v1,v2,v3,v4,v5,v6) in sg_rows:
        if v1 not in sgs:
            t1 = v1.encode()
            sgs[t1] = {}
            sgs[t1]['Inbound'] = []
            sgs[t1]['Outbound'] = []
            sgs[t1]['resource'] = None
#    pp(sgs)
#
# Now create the security groups in AWS. We will need to identify them with a human readable name
#
#    createSecurityGroups(sgs, vpcId)
#
# Now add in the rules where they belong in the dictionary
# If the rule references a source in the Address table space
# then the set of addresses built previously is attached to the rule.
# If the source is not found in the Address table space then
# a marker is created that will be filled in with the appropriate
# AWS security group resource Id after the resource groups are created.
#
    count = 0
    for (var1, var2, var3, var4, var5, var6) in sg_rows:
        rule = 'rule' + str(count)
#        result[rule]             = {}
#        result[rule]['Name']     = var1.encode()
#        result[rule]['Direction']= var2.encode()
#        result[rule]['Protocol'] = var3.encode()
#        result[rule]['port']     = var4.encode()
#        result[rule]['source']   = var5.encode()
#        pp(result)
        temp = {}
        temp['FromPort'] = int(var4.encode())
        temp['IpProtocol'] = var3.encode()
        temp['UserIdGroupPairs'] = []
        temp['IpRanges'] = []
        if var5.encode() in ipAddrs:
#            temp['IpRanges'].append(ipAddrs[var5.encode()])
            temp['IpRanges'] = ipAddrs[var5.encode()]
        else:
            temp['UserIdGroupPairs'].append({'GroupId': var5.encode(), 'UserId': AWSuserId})
        temp['Ipv6Ranges'] = []
        temp['PrefixListIds'] = []
        temp['ToPort'] = int(var4.encode())
        sgs[var1][var2.encode()].append(temp)
        count = count + 1
    return sgs

def getServerInfo():
    result = {}
    placeHolder = " "
    productionValue = "0"
    query = ("SELECT * FROM server_defs")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, ())
    rows = vpcCursor.fetchall()
    count = 0
    for (var1, var2, var3, var4, var5, var6, var7, var8, var9, var10) in rows:
#        srvr = 'server' + str(count)
        srvr = var1.encode()
        result[srvr]              = {}
#        result[srvr]['Name']      = var1.encode()
        result[srvr]['AMI']       = var2.encode()
        result[srvr]['AMI_Id']    = None
        result[srvr]['InstType']  = var3.encode()
        result[srvr]['subnet']    = var4.encode()
        result[srvr]['mainStorage']  = var5
        result[srvr]['extraStorage'] = var6
        result[srvr]['securityGroup']= var7.encode()
        result[srvr]['securityKey']  = var8.encode()
        if var9 != None:
            result[srvr]['localIp']  = var9.encode()
        else:
            result[srvr]['localIp']  = ''
        if var10 != None:
            result[srvr]['startupScript'] = var10.encode()
        else:
            result[srvr]['startupScript'] = ''
        count = count + 1
        
    return result


def getSubnetInfo():
   result = {}
   placeHolder = " "
   productionValue = "0"
   query = ("SELECT * FROM subnets")
   vpcCursor = cnx.cursor()
   vpcCursor.execute(query, ())
   rows = vpcCursor.fetchall()
   count = 0
   for (var1, var2, var3, var4, var5) in rows:
#      net = 'subnet' + str(count)
      net = var1.encode()
      result[net]            = {}
      result[net]['Name']    = var1.encode()
      result[net]['CIDR']    = var2.encode()  + "/" + var3.encode()
      result[net]['pubPriv'] =  var4
      result[net]['descr']   = var5.encode()
      result[net]['sNet_Id'] = None
      count = count + 1
   return result

def getVPCInfo(productionValue ):
   result = {}
   placeHolder = " "
   query = ("SELECT * FROM vpc WHERE Production = %s %s")
   vpcCursor = cnx.cursor()
   vpcCursor.execute(query, (productionValue, placeHolder))
#
# There should only be one but...
#
   count = 0
   rows = vpcCursor.fetchall()
   for (var1, var2, var3, var4) in rows:
      vpc = 'vpc' + str(count)
      result[vpc] = {}
      result[vpc]['region'] = var1.encode()
      result[vpc]['CIDR'] = var2.encode()  + "/" + var3.encode()
      result[vpc]['production'] = var4
      count = count + 1
   return result

#
# get a requested value from the table "keypairs"
#
def queryKeyPairs(keyValue):
    result = None
    placeHolder = " "
    query = ("SELECT tokenValue FROM keypairs WHERE tokenKey = %s %s")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, (keyValue, placeHolder))
    count = 0
    rows = vpcCursor.fetchall()
    for (var1) in rows:
#
# var1 is coming back as a tuple. (use "print type(var1)" to see it)
# Typically there is more than one variable being returned and this
# statement removes them from the tuple. But for some reason this
# single variable is left as a tuple. This MAY be different in Python 3.x
#
# This is a special case because there is only one element to the row returned
# since there is one one item (the 0th item)
# just grab it and make it a string (it is unicode)
#
        it = str(var1[0])
        result = it
    return result

def loadRegionTable():
    result = []
    placeHolder = " "
    query = ("SELECT abbrv, descr, AWSRegion, cidr_base, cidr_range FROM regions Where %s %s")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, ("1", placeHolder))
    count = 0
    rows = vpcCursor.fetchall()
    for (var1, var2, var3, var4, var5) in rows:
        entry = var1.encode()
        result.append({})
        result[count]['abbrv'] = var1.encode()
        result[count]['descr'] = var2.encode()
        result[count]['AWSRegion'] = var3.encode()
        result[count]['CIDR'] = ''.join([var4.encode(), '/', var5.encode()])
        count = count + 1

    return result

def getRegionFromAbbrv(reqRegion):
    result = None
    placeHolder = " "
    query = ("SELECT AWSRegion, cidr_base, cidr_range FROM regions WHERE abbrv = %s %s")
    vpcCursor = cnx.cursor()
    vpcCursor.execute(query, (reqRegion, placeHolder))
    count = 0
    rows = vpcCursor.fetchall()
    for (var1, var2, var3) in rows:
        result = {}
        result['Region'] = var1.encode()
        result['CIDR'] = var2.encode() + '/' + var3.encode()
    return result
