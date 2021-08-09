# -*- coding: utf-8 -*-

from edi.substanceforms import _
from Products.Five.browser import BrowserView
from plone import api as ploneapi

class DatenbankView(BrowserView):

    def __call__(self):
        self.objectlist = self.context.getFolderContents()
        return self.index()

