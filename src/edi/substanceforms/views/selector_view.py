# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from plone import api as ploneapi


class SelectorView(BrowserView):
    def __call__(self):

        viewname = "%s-form-view" % self.context.tablename
        view = ploneapi.content.get_view(
            name=viewname,
            context=self.context,
            request=self.request)

        url = "%s/@@%s" % (self.context.absolute_url(), viewname)
        return self.request.response.redirect(url)
