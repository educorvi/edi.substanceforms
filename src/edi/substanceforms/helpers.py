# -*- coding: utf-8 -*-
from edi.substanceforms.vocabularies import vocabularies

def check_value(value):
    if not value:
        return 'NULL'

def get_vocabulary(attribute):
    return vocabularies.get(attribute, [])
