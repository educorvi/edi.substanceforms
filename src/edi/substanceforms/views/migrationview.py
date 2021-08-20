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

    def __call__(self):

        template = '''<li class="heading" i18n:translate="">
                  Migration erfolgreich
                </li>'''

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

        import pdb; pdb.set_trace()

        print("Starting data migration...")
        hostname = self.host
        username = self.username
        password = self.password
        database = self.dbname

        erg = getHersteller()
        # erg2 = getMachines()
        erg3 = getPowders()
        erg4 = getEtiketten()
        erg5 = getManuell()
        erg6 = getProduktdatenblatt()
        erg7 = getHeatset()
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        for i in erg:
            hersteller_title = i.get('title')
            hersteller_desc = i.get('description')
            hersteller_uid = i.get('UID')
            hersteller_homepage = i.get('homepage')
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute("INSERT INTO manufacturer (title, description, webcode, homepage) VALUES (%s, %s, %s, %s);",
                        (hersteller_title, hersteller_desc, hersteller_uid, "www.test.de"))
            conn.commit()
            # print(hersteller_title)# correct
            cur.close()

        print('Successfully migrated MANUFACTURER')


        return template
