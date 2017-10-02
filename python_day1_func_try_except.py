#!/usr/bin/python

import os
import sys, json, pprint

def process_json_file(filename):
  try:
    with open(filename) as json_file:
      pp_descr = json.load(json_file)
      for keyval in pp_descr:
        print keyval, len(pp_descr[keyval])
        if keyval == 'app' or keyval == 'alert' or keyval == 'event_policy':
          pass
          pprint.pprint(pp_descr[keyval])
  except Exception as exc:
    print 'function -', sys._getframe().f_code.co_name, 'Caught Exception:', exc


def process_json_file_b(filename):
  path = './' + filename
  pp_descr = None
  file_p   = None
  if os.path.isfile(path) and os.access(path, os.R_OK):
#    print "File exists and is readable"
    file_p   = open(path)
    pp_descr = json.load(file_p)
    for keyval in pp_descr:
      print keyval, len(pp_descr[keyval])
      if keyval == 'app' or keyval == 'alert' or keyval == 'event_policy':
        pprint.pprint(pp_descr[keyval])
    file_p.close()
  else:
    print "Either file is missing or is not readable"


process_json_file(filename='powerpack.json')
raw_input('Please press "Enter"')
process_json_file_b('powerpack.json')
raw_input('Please press "Enter"')
process_json_file('notArealFile')
process_json_file_b('notArealFile')



print 'Bye-Bye'

