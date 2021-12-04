# -*- coding: utf-8 -*-
from edi.substanceforms.testing import EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING
from edi.substanceforms.testing import EDI_SUBSTANCEFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')

    def test_migrationview_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='migrationview'
        )
        self.assertTrue(view.__name__ == 'migrationview')

class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
