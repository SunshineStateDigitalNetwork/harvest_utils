#!/usr/bin/env python3

import sys
import json
import shutil
import argparse


def add_json(source, target):
    shutil.move(target, target + '.bak')
    with open(target, 'w') as json_out:
        target_file = open(target + '.bak')
        target_json = json.load(target_file)
        source_file = open(source)
        source_json = json.load(source_file)
        for rec in source_json:
            target_json.append(rec)
        json.dump(target_json, json_out)
        target_file.close()
        source_file.close()
        

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('source', help='JSON document with records to add')
    p.add_argument('destination', help='JSON document to append records to')
    args = p.parse_args()
    add_json(args.source, args.destination)
    