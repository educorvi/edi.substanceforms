# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import jsonlib
from edi.substanceforms.lib import DBConnect


class Gefahrstoff(BrowserView):
    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username, password=self.context.password)

        #gemischid = self.request.get('gefahrstoffid')
        gemischid = "https://emissionsarme-produkte.bgetem.de/datenbank-chemie-dp/wasch-und-reinigungsmittel-fuer-den-etikettendruck/biolon-xi-fluessig"
        if gemischid.startswith('https://'):
            select = "SELECT mixture_id FROM oldlinks WHERE link = %s" % gemischid
            mixture_id = self.db.execute(select)
        else:
            mixture_id = gemischid.split('.')[-1]


        import pdb; pdb.set_trace()

        gefahrstoffdata = {}



        return gefahrstoffdata
