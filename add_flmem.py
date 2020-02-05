#!/usr/bin/env python3

import json
import sys
import datetime

with open('/opt/ssdn/ssdn_data/SSDN-{}.json'.format(datetime.date.today()),
          'w') as json_out:
    doc = open(sys.argv[1])
    doc_json = json.load(doc)
    flmem = open('/opt/ssdn/ssdn_data/inc/flmem.rolling.json')
    flmem_json = json.load(flmem)
    for rec in flmem_json:
        doc_json.append(rec)
    json.dump(doc_json, json_out)
    doc.close()
    flmem.close()
    
