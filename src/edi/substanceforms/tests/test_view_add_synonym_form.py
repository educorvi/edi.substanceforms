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
        api.content.create(self.portal, 'Datenbank', 'test-datenbank')
        api.content.create(self.portal['test-datenbank'], 'Tabelle', 'test-tabelle')

    def test_substance_mixture_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal['test-datenbank']['test-tabelle'], self.portal.REQUEST),
            name='add-synonym-form'
        )
        self.assertTrue(view.__name__ == 'add-synonym-form')

    def test_substance_mixture_view_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['test-datenbank'], self.portal.REQUEST),
                name='add-synonym-form'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
