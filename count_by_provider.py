#!/usr/bin/env python3

import sys, json
from collections import Counter

data_providers = []

with open(sys.argv[1]) as f:
    rec = json.load(f)
    for record in rec:
        data_providers.append(record['dataProvider'])

counts = Counter(data_providers)

for item in list(counts):
    print(item, ': ', counts[item])

