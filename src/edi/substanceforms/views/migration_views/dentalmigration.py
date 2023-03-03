# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import random
import datetime
from wtforms import Form, StringField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value, umlaut_handler
from plone import api as ploneapi
import requests
from requests.auth import HTTPBasicAuth
import psycopg2
import csv

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
                       'path': '/praevention/datenbanken/gefahrstoffe/dentaltechnik',
                       'sort_on': 'sortable_title',
                       'metadata_fields': 'UID'}
            entries = getCatalogData(payload)
            newentries = list()
            for i in entries:
                data = getItemData(i)
                newentries.append(data)
                # import pdb; pdb.set_trace()
                print("Fetched DENTAL: " + i.get('title'))
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

        erg = getDental()

        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        for i in erg:
            dental_title = i.get('title')
            dental_desc = i.get('description')
            dental_uid = get_webcode(self)
            dental_skin_category = i.get('hskategorie')
            dental_review_state = i.get('review_state')


            if dental_review_state == 'published':
                dental_published = 'published'
            else:
                dental_published = 'private'

            if i.get('hersteller'):
                dental_manufacturer_name = i.get('hersteller')
                cur = conn.cursor()
                cur.execute(
                    "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(dental_manufacturer_name))
                dental_manufacturer_id = cur.fetchall()
                cur.close()

                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, skin_category, manufacturer_id, status) VALUES (%s, %s, %s, 'dentaltechnik', 'dental', %s, %s, %s);",
                    (dental_title, dental_desc, dental_uid, dental_skin_category,
                     dental_manufacturer_id[0], dental_published))
                conn.commit()
                # print(etikett_title)  # correct
                cur.close()

                print(dental_title)
            else:
                print("Dumm gelaufen")




        print('Successfully migrated DENTAL')


        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')


        return template
