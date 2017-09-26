#/bin/python

import sys, json, pprint

def process_json_file(filename):
  try:
    with open('.digest') as json_file:
      pp_descr = json.load(json_file)
      for keyval in pp_descr:
        print keyval, len(pp_descr[keyval])
        if keyval == 'app' or keyval == 'alert' or keyval == 'event_policy':
          pass
          pprint.pprint(pp_descr[keyval])
  except Exception as exc:
    print 'function -', sys._getframe().f_code.co_name, 'Caught Exception:', exc


def process_json_file_b(filename):
  try:
    pp_descr = None
    file_p   = None
    file_p   = open(filename)
    pp_descr = json.load(file_p)
    for keyval in pp_descr:
      print keyval, len(pp_descr[keyval])
      if keyval == 'app' or keyval == 'alert' or keyval == 'event_policy':
        pprint.pprint(pp_descr[keyval])
    file_p.close()
  except Exception as exc:
    print 'function -', sys._getframe().f_code.co_name, 'Caught Exception:', exc



process_json_file(filename='powerpack.json')
process_json_file_b('powerpack.json')

process_json_file('notArealFile')



print 'Bye-Bye'


