# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class SelectorView(BrowserView):
    def __call__(self):

        viewname = "%s-form-view" % self.context.tablename
        view = ploneapi.content.get_view(
            name=viewname,
            context=self.context,
            request=self.request
        )

        if view:
            url = "%s/@@%s" % (self.context.absolute_url(), viewname)
            return self.request.response.redirect(url)

        return self.request.response.redirect(self.context.absolute_url())
