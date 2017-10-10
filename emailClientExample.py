#!/usr/bin/python

import io
import os
import sys
import json
import poplib
import pprint
import select
import subprocess
import datetime
import time

import email
from email.parser import Parser

from emailProc import html_parser

pp = pprint.PrettyPrinter(indent=4)

user = "emailtestaccount@earthlink.net"
pwd  = "NotTellingYou"

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))


def email_process():
#    M = poplib.POP3('pop.earthlink.net')
    M = poplib.POP3_SSL('mail.cisco.com')
#    M = poplib.POP3('mail.cisco.com')
    M.user(user)
    M.pass_(pwd)
    numMessages = len(M.list()[1])
    
    print("There are {} message(s) on the server".format(numMessages))
    
    for i in range(numMessages):
        processError = True
        print
        print("Message #{}:   **********************************".format(i))
        msg = ""
        for j in M.retr(i+1)[1]:
            msg += j + '\n'

        headers = Parser().parsestr(msg)
        msgSubject = headers['Subject']
        print("Message {} Subject: {}".format(i, msgSubject))   
        emsg = email.message_from_string(msg)
        
        print(msgSubject)
#        print(emsg)
        if ( "COI services are ready for provisioning" in msgSubject ):
            print("Found provisioning email")
            if emsg.is_multipart():
                print("Is multi-part")
                for payload in emsg.get_payload():
                    if payload.is_multipart():
                        for innerPayload in payload.get_payload():
                            if innerPayload.is_multipart():
                                for innerMore in innerPayload.get_payload():
                                    cType = innerMore.get_content_type()
                                    if cType == "text/html":
                                        pass
                                        print("L3 - Found HTML embedded in message")
                                        processError = True
#                                        print("123456789{}".format(innerPayload.get_payload(decode=True)))
                            else:
                                cType = innerPayload.get_content_type()
                                if cType == "text/html":
                                    print("L2 - Found HTML embedded in message")
                                    html_parser(innerPayload.get_payload(decode=True))
                                    processError = True
#                                    print("987654321 - {}".format(innerPayload.get_payload(decode=True)))
                
                    else:
                        cType = payload.get_content_type()
                        if cType == "text/html":
                            print("L1 - Found HTML embedded in message")
                            html_parser(payload.get_payload(decode=True))
                            processError = True
#                            print(payload.get_payload(decode=True))
            else:
#                print("Not a multi-part message")
#                print(emsg.is_multipart())
#                print(emsg.get_content_type())
#                dump(emsg)
#                print(emsg)
                payload = emsg.get_payload(decode=True)
#                payload = emsg.get_payload()
#                print(payload)
#                print(payload)
                html_parser(payload)

        if processError == False:
            print("Processing successful - Deleteing message #{}".format(i+1))
#            M.dele(i+1)

#
# Commit the changes (deletes) and releases the connection
#
    M.quit()


if __name__ == "__main__":
    sys.exit(email_process())
