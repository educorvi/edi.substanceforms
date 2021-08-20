# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import requests
import random
import datetime
from wtforms import Form, StringField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
import requests
import psycopg2

class Migrationview(BrowserView):

    login = {'login': 'restaccess', 'password': 'H9jCg768'}
    authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
    searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

    self.host = self.context.aq_parent.host
    self.dbname = self.context.aq_parent.database
    self.username = self.context.aq_parent.username
    self.password = self.context.aq_parent.password

    def getAuthToken():
        headers = {'Accept': 'application/json'}
        token = requests.post(authurl, headers=headers, json=login)
        return token.json().get('token')

    def getCatalogData(query):
        token = getAuthToken()
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % token,
        }
        results = requests.get(searchurl, headers=headers, params=query)
        return results.json().get('items')

    def getItemData(entry):
        token = getAuthToken()
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % token,
        }
        results = requests.get(entry.get('@id'), headers=headers)
        return results.json()

    def possibleGefahrstoffe():
        terms = []
        payload = {'portal_type': 'nva.chemiedp.produktdatenblatt',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        for i in entries:
            print(i)

    def getHersteller():
        payload = {'portal_type': 'nva.chemiedp.hersteller',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            print("Fetched MANUFACTURER: " + i.get('title'))
        return newentries

    def getPowders():
        payload = {'portal_type': 'nva.chemiedp.druckbestaeubungspuder',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            print("Fetched POWDER: " + i.get('title'))
        return newentries

    def getEtiketten():
        payload = {'portal_type': 'nva.chemiedp.reinigungsmitteletiketten',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            # import pdb; pdb.set_trace()
            print("Fetched DETERGENT_LABEL: " + i.get('title'))
        return newentries

    def getManuell():
        payload = {'portal_type': 'nva.chemiedp.reinigungsmittelmanuell',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            print("Fetched DETERGENT_MANUAL: " + i.get('title'))
        return newentries

    def getProduktdatenblatt():
        payload = {'portal_type': 'nva.chemiedp.produktdatenblatt',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            print("Fetched PRODUCT_DATASHEET: " + i.get('title'))
        return newentries

    def getHeatset():
        payload = {'portal_type': 'nva.chemiedp.heatsetwaschmittel',
                   'b_size': 500,
                   'sort_on': 'sortable_title',
                   'metadata_fields': 'UID'}
        entries = getCatalogData(payload)
        newentries = list()
        for i in entries:
            data = getItemData(i)
            newentries.append(data)
            print("Fetched DETERGENT_HEATSET: " + i.get('title'))
        return newentries

    def __call__(self):
        import pdb; pdb.set_trace()

        def getAuthToken():
            headers = {'Accept': 'application/json'}
            token = requests.post(authurl, headers=headers, json=login)
            return token.json().get('token')

        return self.index()
