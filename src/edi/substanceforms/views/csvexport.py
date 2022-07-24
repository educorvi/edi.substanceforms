# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from edi.substanceforms.lib import DBConnect
import csv


class Csvexport(BrowserView):
    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username,
                            password=self.context.password)
        template = '''<li class="heading" i18n:translate="">
          Sample View
        </li>'''

        mixtureselect = "SELECT * FROM substance_mixture"
        mixtures = self.db.execute(mixtureselect)

        import pdb; pdb.set_trace()




        return template
