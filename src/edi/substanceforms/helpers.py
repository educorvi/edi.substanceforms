# -*- coding: utf-8 -*-
from edi.substanceforms.vocabularies import vocabularies

def check_value(value):
    if not value:
        return 'NULL'
    if isinstance(value, list):
        return 'NULL'
    if value == 'None':
        return 'NULL'
    return "'%s'" % value

def list_handler(liste):
    result = '@'.join(liste)
    return result

def reverse_list_handler(liste):
    result = liste.split('@')
    return result

def new_list_handler(liste):
    result = list()
    variable = 0
    for i in liste:
        result.append(liste[variable][0])
        variable = variable + 1
    return result

def get_vocabulary(attribute):
    return vocabularies.get(attribute, [])

def new_list_handler2(liste):
    result = list()
    variable = 0
    vocabulary = get_vocabulary('application_areas')
    for i in liste:
        for v in vocabulary:
            if v[1] == i[0]:
                result.append(v[0])
    return result

def new_list_handler3(liste):
    result = list()
    variable = 0
    vocabulary = get_vocabulary('usecases')
    for i in liste:
        for v in vocabulary:
            if v[1] == i[0]:
                result.append(v[0])
    return result
