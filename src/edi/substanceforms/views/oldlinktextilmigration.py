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
from requests.auth import HTTPBasicAuth

authtuple = ('admin', 'Bg2011eteM')

class Migrationview(BrowserView):

    def __call__(self):

        template = '''<li class="heading" i18n:translate="">
                  Migration erfolgreich
                </li>'''

        login = {'login': 'admin2', 'password': 'H9jCg768'}
        authurl = u'http://praevention-bgetem.bg-kooperation.de/@login'
        searchurl = u'http://praevention-bgetem.bg-kooperation.de/@search'

        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password

        def getCatalogData(query):
            headers = {
                'Accept': 'application/json',
            }
            results = requests.get(searchurl, headers=headers, params=query, auth=HTTPBasicAuth('bgetem', 'rhein'))
            return results.json().get('items')

        def getItemData(entry):
            headers = {
                'Accept': 'application/json',
            }
            results = requests.get(entry.get('@id'), headers=headers, auth=HTTPBasicAuth('bgetem', 'rhein'))
            return results.json()

        def getDental():
            payload = {'portal_type': 'Gefahrstoff',
                       'b_size': 500,
                       'path': '/praevention/datenbanken/gefahrstoffe/textil-und-mode',
                       'sort_on': 'sortable_title',
                       'metadata_fields': 'UID'}
            entries = getCatalogData(payload)
            newentries = list()
            for i in entries:
                data = getItemData(i)
                newentries.append(data)
                # import pdb; pdb.set_trace()
                print("Fetched TEXTILE: " + i.get('title'))
            return newentries


        print("Starting data migration...")
        hostname = self.host
        username = self.username
        password = self.password
        database = self.dbname

        erg = getDental()
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)


        for i in erg:
            textil_title = i.get('title')
            textil_link = i.get('@id')

            cur = conn.cursor()
            cur.execute(
                "SELECT substance_mixture_id FROM substance_mixture WHERE title = '{0}';".format(textil_title))
            textil_ids = cur.fetchall()
            cur.close()

            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO oldlinks (mixture_id, link) VALUES (%s, %s);",
                    (textil_ids[0][0], textil_link))
                conn.commit()
                cur.close()
            except:
                print(textil_title)


        print('Successfully migrated TEXTILE')

        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')


        return template
