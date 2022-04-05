# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import jsonlib
from edi.substanceforms.lib import DBConnect




class Gefahrstoffliste(BrowserView):
    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username, password=self.context.password)

        mixtures = []
        select = "SELECT substance_mixture_id, title FROM substance_mixture WHERE status = 'published';"
        gemische = self.db.execute(select)
        for gemisch in gemische:
            mixture_entry = {}
            selectoldid = "SELECT link FROM oldlinks WHERE mixture_id = %s" % gemisch[0]
            oldid = self.db.execute(selectoldid)
            if oldid:
                mixture_entry['@id'] = oldid
            else:
                mixture_entry['@id'] = "bgetem.substance_mixture."+str(gemisch[0])  # über die Punkt-Notation könnten mehrere potenzielle Quellen angezapft werden
            mixture_entry['title'] = gemisch[1]
            mixtures.append(mixture_entry)
        return jsonlib.write(mixtures)
