# -*- coding: utf-8 -*-

from edi.substanceforms import _
from Products.Five.browser import BrowserView

class DatenbankView(BrowserView):

    def __call__(self):
        self.objectlist = self.context.listFolderContents(contentFilter={"portal_type" : "Datenbank"})
        return self.index()
