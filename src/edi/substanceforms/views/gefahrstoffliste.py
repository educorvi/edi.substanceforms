# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
import jsonlib
from edi.substanceforms.lib import DBConnect

class Gefahrstoffliste(BrowserView):

    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username, password=self.context.password)
        self.db.connect()
        mixtures = []
        select = "SELECT substance_mixture_id, title FROM substance_mixture;"
        gemische = self.db.execute(select)
        for gemisch in gemische:
            mixture_entry = {}
            selectoldid = "SELECT link FROM oldlinks WHERE mixture_id = %s" % gemisch[0]
            oldid = self.db.execute(selectoldid)
            if oldid:
                mixture_entry['@id'] = oldid[0][0]
            else:
                mixture_entry['@id'] = "bgetem.substance_mixture."+str(gemisch[0])  #Namespace für die potenzielle Abfrage mehrerer Quellen
            mixture_entry['title'] = gemisch[1]
            mixtures.append(mixture_entry)
        conn.close()
        return jsonlib.write(mixtures)
