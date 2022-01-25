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

def new_list_handler2(liste):
    result = list()
    variable = 0
    for i in liste:
        cur = conn.cursor()
        cur.execute(
            "SELECT application_area_id FROM application_areas WHERE application_area_name = '{0}';".format(i))
        areaid = cur.fetchall()
        cur.close()

def get_vocabulary(attribute):
    return vocabularies.get(attribute, [])
