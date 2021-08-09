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
        api.content.create(self.portal, 'Document', 'front-page')

    def test_substance_mixture_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='substance_mixture_view'
        )
        self.assertTrue(view.__name__ == 'substance_mixture_view')
        # self.assertTrue(
        #     'Sample View' in view(),
        #     'Sample View is not found in substance_mixture_view'
        # )

    def test_substance_mixture_view_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['front-page'], self.portal.REQUEST),
                name='substance_mixture_view'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
