#!/usr/bin/env python3

import sys, json
from collections import Counter

data_providers = []

with open(sys.argv[1]) as f:
    for line in f:
        rec = json.loads(line)
        #for record in rec:
        data_providers.append(rec['dataProvider'])

counts = Counter(data_providers)

for item in list(counts):
    print(item, ': ', counts[item])

