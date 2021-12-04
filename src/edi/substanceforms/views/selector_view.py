# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from plone import api as ploneapi


class SelectorView(BrowserView):
    def __call__(self):

        viewname = "%s-form-view" % self.context.tablename
        #if self.context.tablename == 'substance_mixture':
            #if self.context.nochzudefinieren == "Etiketten":
                #viewname="etiketten-form-view"

        try:
            view = ploneapi.content.get_view(
                name=viewname,
                context=self.context,
                request=self.request
            )
        except:
            return self.request.response.redirect(self.context.absolute_url()+"/@@tabelle_view")

        url = "%s/@@%s" % (self.context.absolute_url(), viewname)
        return self.request.response.redirect(url)
