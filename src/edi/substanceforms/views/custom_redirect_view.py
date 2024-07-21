# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from plone import api


class CustomRedirectView(BrowserView):
    def __call__(self):
        url = api.portal.get().absolute_url()
        parent = self.context.aq_parent
        if parent:
            url = parent.absolute_url()
        if not api.user.is_anonymous():
            url = self.context.absolute_url() + '/datenbank-view'
        return self.request.response.redirect(url)
