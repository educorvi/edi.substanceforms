# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase
from plone import api as ploneapi

class SubstanceTabelleViewlet(ViewletBase):

    def update(self):
        pass

    def get_tablescript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/tabelle.js'

    def get_searchscript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/search.js'

    def get_hiddenscript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/hidden.js'

    def render(self):
        return super(SubstanceTabelleViewlet, self).render()
