# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import jsonlib
from edi.substanceforms.lib import DBConnect


class Gefahrstoff(BrowserView):
    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username, password=self.context.password)

        gemischid = self.request.get('gemischid')
        #gemischid = "https://emissionsarme-produkte.bgetem.de/datenbank-chemie-dp/wasch-und-reinigungsmittel-fuer-den-etikettendruck/biolon-xi-fluessig"
        if gemischid.startswith('https://'):
            select = "SELECT mixture_id FROM oldlinks WHERE link = '%s'" % gemischid
            mixture_id = self.db.execute(select)
        else:
            mixture_id = gemischid.split('.')[-1]

        mixture_id = mixture_id[0][0]

        data1select = "SELECT * FROM substance_mixture WHERE substance_mixture_id = %s" % mixture_id
        data1 = self.db.execute(data1select)
        data2select = "SELECT * FROM manufacturer WHERE manufacturer_id = %s" % data1[0][25]
        data2 = self.db.execute(data2select)
        data3select = "SELECT * FROM recipes WHERE mixture_id = %s" % mixture_id
        data3 = self.db.execute(data3select)

        gefahrstoffdata = {}

        hersteller = {}
        hersteller['title'] = data2[0][1]
        hersteller['@id'] = "bgetem.manufacturer."+str(data2[0][0])
        hersteller['description'] = data2[0][2]
        hersteller['homepage'] = data2[0][4]

        inhaltsstoffe = list()
        for inhalt in data3:
            inhaltsstoff = {}
            select = "SELECT * FROM substance WHERE substance_id = %s" % inhalt[1]
            reinstoff = self.db.execute(select)
            import pdb;
            pdb.set_trace()
            inhaltsstoff['cas'] = reinstoff[0][4]
            inhaltsstoff['gefahrstoff'] = reinstoff[0][1]
            inhaltsstoff['anteil_min'] = inhalt[3]
            inhaltsstoff['anteil_max'] = inhalt[4]
            inhaltsstoff['anteil'] = f">= {inhalt[3]}% - <= {inhalt[4]}%"
            inhaltsstoffe.append(inhaltsstoff)

        productclassselect = "SELECT class_name FROM productclasses WHERE class_id = %s" % data1[0][27]
        try:
            productclass = self.db.execute(productclassselect)
        except:
            productclass = None

        produktkategorien = {
            "label": "Reinigungsmittel im Etikettendruck",
            "offset": "Offsetdruck allgemein",
            "heatset": "Heatsetwaschmittel",
            "uv": "Reinigungsmittel im UV-Druck",
            "special": "Sonderreiniger"
        }

        produktkategorie = list()
        produktkategorie.append(produktkategorien[data1[0][5]])

        gefahrstoffdata['hersteller'] = hersteller
        gefahrstoffdata['hskategorie'] = data1[0][16]
        gefahrstoffdata['bemerkungen'] = data1[0][23]
        gefahrstoffdata['chemikalienliste'] = inhaltsstoffe
        gefahrstoffdata['UID'] = data1[0][3]
        gefahrstoffdata['title'] = data1[0][1]
        gefahrstoffdata['review_state'] = data1[0][26]
        gefahrstoffdata['emissionsgeprueft'] = data1[0][17]
        gefahrstoffdata['produktkategorie'] = produktkategorie
        gefahrstoffdata['description'] = data1[0][2]
        gefahrstoffdata['wertebereich'] = data1[0][20]
        gefahrstoffdata['flammpunkt'] = data1[0][19]
        gefahrstoffdata['@id'] = gemischid
        gefahrstoffdata['produktklasse'] = productclass


        import pdb; pdb.set_trace()

        return jsonlib.write(gefahrstoffdata)
