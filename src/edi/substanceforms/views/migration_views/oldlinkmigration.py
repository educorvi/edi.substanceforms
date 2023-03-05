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
import csv

authtuple = ('admin', 'Bg2011eteM')

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
            }
            results = requests.get(searchurl, headers=headers, params=query, auth=authtuple)
            return results.json().get('items')

        def getItemData(entry):
            token = getAuthToken()
            headers = {
                'Accept': 'application/json',
            }
            results = requests.get(entry.get('@id'), headers=headers, auth=authtuple)
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

        def check_webcode(self, generated_webcode):
            host = self.host
            dbname = self.dbname
            username = self.username
            password = self.password

            conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
            cur = conn.cursor()
            select = """SELECT tablename from pg_catalog.pg_tables WHERE schemaname != 'pg_catalog'
                        AND schemaname != 'information_schema';"""
            cur.execute(select)
            tables = cur.fetchall()
            cur.close()

            for i in tables:
                table = i[0]
                if table == 'manufacturer' or table == 'substance' or table == 'substance_mixture' or table == 'spray_powder':
                    cur = conn.cursor()
                    select = "SELECT webcode from %s WHERE webcode = '%s'" % (table, generated_webcode)
                    cur.execute(select)
                    erg = cur.fetchall()
                    cur.close()
                else:
                    erg = False
                if erg:
                    return False
            self.db.close()
            return True

        def get_webcode(self, webcode=False):
            while not webcode:
                random_number = random.randint(100000, 999999)
                shortyear = datetime.datetime.now().strftime('%Y')[2:]
                generated_webcode = "PD%s%s" % (shortyear, random_number)
                webcode = check_webcode(self, generated_webcode)
                if webcode:
                    return generated_webcode

        print("Starting data migration...")
        hostname = self.host
        username = self.username
        password = self.password
        database = self.dbname

        erg4 = getEtiketten()
        erg5 = getManuell()
        erg6 = getProduktdatenblatt()
        erg7 = getHeatset()
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)


        for i in erg4:
            etikett_title = i.get('title')
            etikett_link = i.get('@id')

            cur = conn.cursor()
            cur.execute(
                "SELECT substance_mixture_id FROM substance_mixture WHERE title = '{0}';".format(etikett_title))
            etikett_ids = cur.fetchall()
            cur.close()

            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO oldlinks (mixture_id, link) VALUES (%s, %s);",
                    (etikett_ids[0][0], etikett_link))
                conn.commit()
                cur.close()
            except:
                print(etikett_title)


        print('Successfully migrated DETERGENT_LABELS')

        for i in erg5:
            manuell_title = i.get('title')
            manuell_link = i.get('@id')

            cur = conn.cursor()
            cur.execute(
                "SELECT substance_mixture_id FROM substance_mixture WHERE title = '{0}';".format(manuell_title))
            manuell_ids = cur.fetchall()
            cur.close()

            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO oldlinks (mixture_id, link) VALUES (%s, %s);",
                    (manuell_ids[0][0], manuell_link))
                conn.commit()
                cur.close()
            except:
                print(manuell_title)

        print('Successfully migrated DETERGENT_MANUAL')

        for i in erg6:
            datenblatt_title = i.get('title')
            datenblatt_link = i.get('@id')

            cur = conn.cursor()
            cur.execute(
                "SELECT substance_mixture_id FROM substance_mixture WHERE title = '{0}';".format(datenblatt_title))
            datenblatt_ids = cur.fetchall()
            cur.close()

            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO oldlinks (mixture_id, link) VALUES (%s, %s);",
                    (datenblatt_ids[0][0], datenblatt_link))
                conn.commit()
                cur.close()
            except:
                print(datenblatt_title)

        print('Successfully migrated PRODUCT_DATASHEET')

        for i in erg7:
            heatset_title = i.get('title')
            heatset_link = i.get('@id')

            cur = conn.cursor()
            cur.execute(
                "SELECT substance_mixture_id FROM substance_mixture WHERE title = '{0}';".format(heatset_title))
            heatset_ids = cur.fetchall()
            cur.close()

            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO oldlinks (mixture_id, link) VALUES (%s, %s);",
                    (heatset_ids[0][0], heatset_link))
                conn.commit()
                cur.close()
            except:
                print(heatset_title)

        print('Successfully migrated DETERGENT_HEATSET')
        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')


        return template
