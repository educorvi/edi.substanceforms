# -*- coding: utf-8 -*-
from edi.substanceforms.vocabularies import vocabularies

def check_value(value):
    if not value:
        return 'NULL'
    if isinstance(value, list):
        return 'NULL'
    return "'%s'" % value

def get_vocabulary(attribute):
    return vocabularies.get(attribute, [])
