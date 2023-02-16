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

        erg3 = getPowders()
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        for i in erg3:
            powder_title = i.get('title')
            powder_desc = i.get('description')
            powder_uid = get_webcode(self)
            powder_link = i.get('@id')
            powder_product_class = i.get('produktklasse')
            powder_starting_material = i.get('ausgangsmaterial')
            powder_median_value = i.get('medianwert')
            powder_volume_share = i.get('volumenanteil')
            powder_checked_emissions = i.get('emissionsgeprueft')
            powder_date_checked = i.get('pruefdateum')
            powder_manufacturer_name = i.get('hersteller')['title']
            powder_review_state = i.get('review_state')

            if powder_review_state == 'published':
                powder_published = 'published'
            else:
                powder_published = 'private'

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(powder_manufacturer_name))
            powder_manufacturer_id = cur.fetchall()
            cur.close()

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO spray_powder (title, description, webcode, manufacturer_id, image_url, product_class, starting_material, median_value, volume_share, checked_emissions, date_checked, status) VALUES (%s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s, %s);",
                (powder_title, powder_desc, powder_uid, powder_manufacturer_id[0], powder_product_class,
                 powder_starting_material, powder_median_value, powder_volume_share, powder_checked_emissions,
                 powder_date_checked, powder_published))
            conn.commit()
            cur.close()

        print('Successfully migrated SPRAY_POWDER')
        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')

        return template
