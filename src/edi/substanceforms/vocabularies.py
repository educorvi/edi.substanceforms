# -*- coding: utf-8 -*-
hskategorie = [
    (u"id_wasserloeslich", u"gegen wasserlösliche Arbeitsstoffe"),
    (u"id_nichtwasserloeslich", u"gegen wasserunlösliche Arbeitsstoffe"),
    (u"id_wechselnd", u"gegen wechselnde Arbeitsstoffe"),
    (u"alle_branchen", u"alle Branchen")
    ]

branchen = [
    (u"druck_und_papier", u"Druck und Papierverarbeitung"),
    (u"elektrohandwerke", u"Elektrohandwerke"),
    (u"elektrotechnische_industrie", u"Elektrotechnische Industrie"),
    (u"energie_und_wasser", u"Energie und Wasserwirtschaft"),
    (u"feinmechanik", u"Feinmechanik"),
    (u"textil_und_mode", u"Textil und Mode"),
    (u"alle_branchen", u"Alle Branchen"),
    ]

substance_types = [
    (u'detergent_labels', u'Reinigungsmittel Etiketten'),
    (u'detergent_heatset', u'Heatsetwaschmittel'),
    (u'detergent_manual', u'Reinigungsmittel manueller Gebrauch'),
    ('product_datasheet', u'Wasch- und Reinigungsmittel für den Offsetdruck'),
    ('offset', u'Wasch- und Reinigungsmittel für den Offsetdruck')
    ]

substance_types_new = [
    (u'label', u'Etikettendruck'),
    (u'uv', u'UV-Druck'),
    (u'heatset', u'Heatsetwaschmittel'),
    ('special', u'Sonderreiniger'),
    ('offset', u'Offsetdruck (allgemein)')
    ]

produktkategorien = [
    (u'konventionell', u'konventioneller Druck'),
    (u'uvdruck', u'UV-Druck')
    ]

produktklassen = [
    (u'waschmittel_pflanzenoel', u'Waschmittel auf Pflanzenölbasis'),
    (u'uv-waschmittel', u'UV-Waschmittel'),
    (u'waschmittel_kohlenwasserstoff', u'Waschmittel auf Kohlenwasserstoffbasis'),
    (u'waschmittel_testbenzin', u'Waschmittel auf Basis von Testbenzin'),
    (u'waschmittel_emulsionen', u'Waschmittel auf wässriger Basis/Emulsionen')
    ]

product_class = [
    (u'fein', u'fein'),
    (u'mittel', u'mittel'),
    (u'grob', u'grob')
    ]

classifications = [
    (u'xi-reizend', u'Xi; Reizend'),
    (u'xn-gesundheitsschaedlich', u'Xn; gesundheitsschädlich'),
    (u'signalwort-achtung', u'Signalwort: Achtung'),
    (u'signalwort-gefahr', u'Signalwort: Gefahr'),
    (u'piktogramm-achtung', u'Piktogramm: Achtung'),
    (u'piktogramm-aetzend', u'Piktogramm: Ätzend'),
    (u'piktogramm-entflammbar', u'Piktogramm: Entflammbar')
    ]

usecases = [
    (1, u'Buchdruck'),
    (2, u'Flexodruck'),
    (3, u'Siebdruck'),
    (4, u'Farbreiniger alle Druckverfahren'),
    (5, u'Offsetdruck'),
    (6, u'Waschanlage'),
    (7, u'Tiefdruck'),
    (8, u'Klebstoffreiniger'),
    (9, u'UV-Druck'),
    (10, u'Klischeereiniger'),
    (11, u'Bodenreiniger'),
    (12, u'Entfetter'),
    (13, u'Reflektorreiniger')
    ]

application_areas = [
    (1, u'Farbreiniger'),
    (2, u'Plattenreiniger'),
    (3, u'Feuchtwalzenreiniger'),
    (4, u'Gummituchregenerierer'),
    (5, u'Reiniger für Leitstände, Sensoren'),
    (6, u'Klebstoffreiniger')
    ]

boolvocab = [
    (u'True', u'Ja'),
    (u'False', u'Nein'),
    (u'None', u'Nein')
    ]

vocabularies = {
        'hskategorie':hskategorie,
        'branch':branchen,
        'substance_types':substance_types,
        'substance_type':substance_types_new,
        'produktkategorien':produktkategorien,
        'produktklassen':produktklassen,
        'classifications':classifications,
        'usecases':usecases,
        'application_areas':application_areas,
        'boolvocab':boolvocab
    }
