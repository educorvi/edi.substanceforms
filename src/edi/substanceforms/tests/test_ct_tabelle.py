# -*- coding: utf-8 -*-
from edi.substanceforms.content.tabelle import ITabelle  # NOQA E501
from edi.substanceforms.testing import EDI_SUBSTANCEFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class TabelleIntegrationTest(unittest.TestCase):

    layer = EDI_SUBSTANCEFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Datenbank',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_tabelle_schema(self):
        fti = queryUtility(IDexterityFTI, name='Tabelle')
        schema = fti.lookupSchema()
        self.assertEqual(ITabelle, schema)

    def test_ct_tabelle_fti(self):
        fti = queryUtility(IDexterityFTI, name='Tabelle')
        self.assertTrue(fti)

    def test_ct_tabelle_factory(self):
        fti = queryUtility(IDexterityFTI, name='Tabelle')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ITabelle.providedBy(obj),
            u'ITabelle not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_tabelle_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Tabelle',
            id='tabelle',
        )

        self.assertTrue(
            ITabelle.providedBy(obj),
            u'ITabelle not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('tabelle', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('tabelle', parent.objectIds())

    def test_ct_tabelle_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Tabelle')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_tabelle_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Tabelle')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'tabelle_id',
            title='Tabelle container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
