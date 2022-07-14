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

def tableheads(cryptoname):
    headnames = {
        "substance_mixture_id": "ID",
        "title": "Titel",
        "description": "Beschreibung",
        "webcode": "Webcode",
        "branch": "Branche",
        "substance_type": "Typ des Gefahrstoffgemisches",
        "offset_print_manner": "Offset Druckverfahren",
        "detergent_special": "Sonderreiniger",
        "application_areas": "Anwendungsbereiche",
        "usecases": "Verwendungszwecke",
        "evaporation_lane_150": "Verdampfungsfaktor Fv (Bahntemperatur 150 °C)",
        "evaporation_lane_160": "Verdampfungsfaktor Fv (Bahntemperatur 160 °C)",
        "evaporation_lane_170": "Verdampfungsfaktor Fv (Bahntemperatur 170 °C)",
        "evaporation_lane_180": "Verdampfungsfaktor Fv (Bahntemperatur 180 °C)",
        "ueg": "Untere Explosionsgrenze (UEG) [g/m³]",
        "response": "Responsefaktor",
        "skin_category": "Hautschutzmittelkategorie",
        "checked_emissions": "Emissionsarmes Produkt",
        "date_checked": "Datum letzte Prüfung",
        "flashpoint": "Flammpunkt [°C]",
        "values_range": "Flammpunkt in Wertebereich",
        "classifications": "Klassifikationen",
        "indicators": "Indikatoren",
        "comments": "Kommentare",
        "image_url": "Bild-URL",
        "manufacturer_id": "Hersteller",
        "status": "Status",
        "productclass": "Produktklasse",
        "product_class": "Produktklasse",
        "starting_material": "Ausgangsmaterial",
        "median_value": "Medianwert [µm]",
        "volume_share": "Volumenanteil < 10 µm [Vol.-%]"
    }
    result = headnames.get(cryptoname)
    if not result:
        return cryptoname
    return result
