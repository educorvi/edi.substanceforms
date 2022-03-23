# -*- coding: utf-8 -*-
from edi.substanceforms.content.preselect import IPreselect  # NOQA E501
from edi.substanceforms.testing import EDI_SUBSTANCEFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class PreselectIntegrationTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Tabelle',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_preselect_schema(self):
        fti = queryUtility(IDexterityFTI, name='Preselect')
        schema = fti.lookupSchema()
        self.assertEqual(IPreselect, schema)

    def test_ct_preselect_fti(self):
        fti = queryUtility(IDexterityFTI, name='Preselect')
        self.assertTrue(fti)

    def test_ct_preselect_factory(self):
        fti = queryUtility(IDexterityFTI, name='Preselect')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IPreselect.providedBy(obj),
            u'IPreselect not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_preselect_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Preselect',
            id='preselect',
        )

        self.assertTrue(
            IPreselect.providedBy(obj),
            u'IPreselect not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('preselect', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('preselect', parent.objectIds())

    def test_ct_preselect_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Preselect')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
