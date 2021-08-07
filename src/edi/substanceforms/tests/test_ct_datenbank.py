# -*- coding: utf-8 -*-
from edi.substanceforms.content.datenbank import IDatenbank  # NOQA E501
from edi.substanceforms.testing import EDI_SUBSTANCEFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class DatenbankIntegrationTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_datenbank_schema(self):
        fti = queryUtility(IDexterityFTI, name='Datenbank')
        schema = fti.lookupSchema()
        self.assertEqual(IDatenbank, schema)

    def test_ct_datenbank_fti(self):
        fti = queryUtility(IDexterityFTI, name='Datenbank')
        self.assertTrue(fti)

    def test_ct_datenbank_factory(self):
        fti = queryUtility(IDexterityFTI, name='Datenbank')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IDatenbank.providedBy(obj),
            u'IDatenbank not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_datenbank_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Datenbank',
            id='datenbank',
        )

        self.assertTrue(
            IDatenbank.providedBy(obj),
            u'IDatenbank not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('datenbank', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('datenbank', parent.objectIds())

    def test_ct_datenbank_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Datenbank')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_datenbank_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Datenbank')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'datenbank_id',
            title='Datenbank container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
