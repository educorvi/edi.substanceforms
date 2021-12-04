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
        api.content.create(self.portal, 'Datenbank', 'test-database')
        api.content.create(self.portal['test-database'], 'Tabelle', 'test-tabelle')

    def test_create_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal['test-database']['test-tabelle'], self.portal.REQUEST),
            name='create-substance_mixture-form'
        )
        self.assertTrue(view.__name__ == 'create-substance_mixture-form')

    def test_create_view_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
               (self.portal['test-database'], self.portal.REQUEST),
                name='create-substance_mixture-form'
            )

class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
