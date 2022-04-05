# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import jsonlib
from edi.substanceforms.lib import DBConnect




class Gefahrstoffliste(BrowserView):
    def __call__(self):
        import pdb; pdb.set_trace()
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)

        mixtures = []
        select = "SELECT substance_mixture_id, title FROM substance_mixture WHERE status == 'published';"
        gemische = self.db.execute(select)
        for gemisch in gemische:
            mixture_entry = {}
            import pdb; pdb.set_trace()
            selectoldid = "SELECT link FROM oldlinks WHERE mixture_id = %s" % gemisch[0]
            #oldid = select oldid from mapping_table where id == gemisch.id
            #if oldid:
            #    mixture_entry['@id'] = oldid
            #else:
            #    mixture_entry[
            #        '@id'] = dbname.tabelname.id  # über die Punkt-Notation könnten mehrere potenzielle Quellen
            #    # angezapft werden
            #mixture_entry['title'] = gemisch.title
            #mixtures.append(mixture_entry)
        return jsonlib.write(mixtures)
