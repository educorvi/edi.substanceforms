# -*- coding: utf-8 -*-
hskategorie = [
    (u"id_wasserloeslich", u"gegen wasserlösliche Arbeitsstoffe"),
    (u"id_nichtwasserloeslich", u"gegen wasserunlösliche Arbeitsstoffe"),
    (u"id_wechselnd", u"gegen wechselnde Arbeitsstoffe")
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
    (u'detergent_labels', u'Etikettendruck'),
    (u'detergent_uv', u'UV-Druck'),
    (u'detergent_heatset', u'Heatsetwaschmittel'),
    ('detergent_special', u'Sonderreiniger'),
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
    (u'buchdruck', u'Buchdruck'),
    (u'flexodruck', u'Flexodruck'),
    (u'siebdruck', u'Siebdruck'),
    (u'farbreiniger_alle_druckverfahren', u'Farbreiniger alle Druckverfahren'),
    (u'offsetdruck', u'Offsetdruck'),
    (u'waschanlage', u'Waschanlage'),
    (u'tiefdruck', u'Tiefdruck'),
    (u'klebstoffreiniger', u'Klebstoffreiniger'),
    (u'uv-offsetdruck', u'UV-Druck'),
    (u'klischeereiniger', u'Klischeereiniger'),
    (u'bodenreiniger', u'Bodenreiniger'),
    (u'entfetter', u'Entfetter'),
    (u'reflektorreiniger', u'Reflektorreiniger')
    ]

application_areas = [
    (u'Farbreiniger', u'Farbreiniger'),
    (u'Plattenreiniger', u'Plattenreiniger'),
    (u'Feuchtwalzenreiniger', u'Feuchtwalzenreiniger'),
    (u'Gummituchregenerierer', u'Gummituchregenerierer'),
    (u'Reiniger_Leitstaende_Sensoren', u'Reiniger für Leitstände, Sensoren'),
    (u'Klebstoffreiniger', u'Klebstoffreiniger')
    ]

boolvocab = [
    (u'True', u'Ja'),
    (u'False', u'Nein'),
    (u'None', u'Nein')
    ]

vocabularies = {
        'hskategorie':hskategorie,
        'branchen':branchen,
        'substance_types':substance_types,
        'produktkategorien':produktkategorien,
        'produktklassen':produktklassen,
        'classifications':classifications,
        'usecases':usecases,
        'application_areas':application_areas,
        'boolvocab':boolvocab
    }
