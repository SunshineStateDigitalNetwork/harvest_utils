import json
import sys

with open(sys.argv[2], 'w') as json_out:
    doc_json = json.load(json_out)
    add_file = open(sys.argv[1])
    add_json = json.load(add_file)
    for rec in add_json:
        doc_json.append(rec)
    json.dump(doc_json, json_out)
    json_out.close()
    add_file.close()
    
