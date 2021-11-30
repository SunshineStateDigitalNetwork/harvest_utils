import sys
import json
import datetime
import dateparser
from os.path import exists

PRETTY_PRINT = 'True'


def write_json_ld(docs):
    """
    Simple writing function.
    Will either create and write to file or append.
    """
    if exists('{0}-{1}.json'.format(sys.argv[1], datetime.date.today())) is True:
        with open('{0}-{1}.json'.format(sys.argv[1], datetime.date.today()), 
                  'r', encoding='utf-8') as jsonInput:
            data_in = json.load(jsonInput)
            for record in docs:
                data_in.append(record)
        with open('{0}-{1}.json'.format(sys.argv[1], datetime.date.today()), 
                  'w', encoding='utf-8') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(data_in, jsonOutput, indent=2)
            else:
                json.dump(data_in, jsonOutput)
    else:
        with open('{0}-{1}.json'.format(sys.argv[1], datetime.date.today()), 
                  'w', encoding='utf-8') as jsonOutput:
            if PRETTY_PRINT is True:
                json.dump(docs, jsonOutput, indent=2)
            else:
                json.dump(docs, jsonOutput)


class Scenario:

    def __init__(self, records):
        self.records = records

    def __getitem__(self, item):
        return self.records[item]

    def __iter__(self):
        for record in self.records:
            yield record

    def __len__(self):
        return len(self.records)

    def __str__(self):
        return f'{self.__class__.__name__}'


class APIScenario(Scenario):

    def __init__(self, url, record_key, count_key=None, page_key=None):
        import requests
        import json
        r = requests.get(url)
        #r.encoding = 'UTF-8'
        data = json.loads(r.text.replace('\\u00a0', ''))
        if count_key:
            record_count = [v for v in self._item_generator(data, count_key)][0]
        self.records = [record for record in self._item_generator(data, record_key)]
        if record_count:
            page = 1
            while len(self.records) < record_count:
                page += 1
                r = requests.get(url + f'&{page_key}={page}')
                #r.encoding = 'UTF-8'
                data = json.loads(r.text.replace('\\u00a0', ''))
                self.records = self.records + [record for record in self._item_generator(data, record_key)]
                continue
        Scenario.__init__(self, self.records)

    def _item_generator(self, json_input, lookup_key):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key:
                    if isinstance(v, list):
                        for i in v:
                            yield i
                    else:
                        yield v
                else:
                    yield from self._item_generator(v, lookup_key)
        elif isinstance(json_input, list):
            for item in json_input:
                yield from self._item_generator(item, lookup_key)


class InternetArchive(APIScenario):

    def __init__(self, collection):
        url = f'https://archive.org/advancedsearch.php?q=collection:{collection}&output=json&rows=100'
        APIScenario.__init__(self, url, 'docs', 'numFound', 'page')
        self.records = [InternetArchiveRecord(record) for record in self.records]


class CitrusRecord:

    def __init__(self, record):
        """
        Generic class for single records
        :param record: Generic record
        """
        self.record = record

    def __str__(self):
        return f'{self.__class__.__name__}, {self.harvest_id}'


class InternetArchiveRecord(CitrusRecord):

    def __init__(self, record):
        CitrusRecord.__init__(self, record)
        self.harvest_id = f'ia:{self.identifier}'

    @property
    def identifier(self):
        return self.record['identifier']

    def __getattr__(self, item):
        return self.record[item]


if __name__ == '__main__':
    collection = sys.argv[1]
    docs =[]
    recs = InternetArchive(collection)
    for rec in recs:
        
        sourceResource = {}
        try:
            if isinstance(rec.contributor, list):
                sourceResource['contributor'] = [{'name': name.strip('.')} for name in rec.contributor]
            else:
                sourceResource['contributor'] = [{'name': rec.contributor.strip('.')}]
        except KeyError:
            pass
        try:
            if isinstance(rec.creator, list):
                sourceResource['creator'] = [{'name': name.strip('.')} for name in rec.creator]
            else:
                sourceResource['creator'] = [{'name': rec.creator.strip('.')}]
        except KeyError:
            pass
        try:
            if rec.date:
                if isinstance(rec.date, list):
                    rec.date = rec.date[0]
                d = dateparser.parse(rec.date, languages=['en']).date().isoformat()
                sourceResource['date'] = {"begin": d, "end": d, "displayDate": d}
        except KeyError:
            pass
        try:
            if rec.description:
                sourceResource['description'] = rec.description.strip(' ')
        except KeyError:
            pass
        sourceResource['identifier'] = 'https://archive.org/details/{}'.format(rec.identifier)
        try:
            if rec.language:
                sourceResource['language'] = rec.language
        except KeyError:
            pass
        sourceResource['rights'] = {'@id': 'http://rightsstatements.org/vocab/NoC-US/1.0/'}
        try:
            if isinstance(rec.subject, list):
                sourceResource['subject'] = [{'name': sub.strip('.')} for sub in rec.subject]
            else:
                sourceResource['subject'] = [{'name': rec.subject.strip('.')}]
        except KeyError:
            pass
        if rec.title:
            sourceResource['title'] = rec.title
        doc = {"@context": "http://api.dp.la/items/context",
               "sourceResource": sourceResource,
               "aggregatedCHO": "#sourceResource",
               "dataProvider": "State Library and Archives of Florida",
               "isShownAt": 'https://archive.org/details/{}'.format(rec.identifier),
               "preview": 'https://archive.org/services/img/{}'.format(rec.identifier),
               "provider": {'name': 'Sunshine State Digital Network',
                                    '@id': 'UNDETERMINED'}}
        
        docs.append(doc)
    write_json_ld(docs)
