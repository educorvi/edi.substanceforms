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
            conn.close()
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

        usecasevocab = ['Buchdruck', 'Flexodruck', 'Siebdruck', 'Farbreiniger alle Druckverfahren', 'Offsetdruck',
                        'Waschanlage', 'Tiefdruck', 'Klebstoffreiniger', 'UV-Druck', 'Klischeereiniger',
                        'Bodenreiniger', 'Entfetter', 'Reflektorreiniger']

        usecasetranslate = {'buchdruck': 'Buchdruck', 'flexodruck': 'Flexodruck', 'siebdruck': 'Siebdruck',
                        'farbreiniger_alle_druckverfahren': 'Farbreiniger alle Druckverfahren',
                        'offsetdruck': 'Offsetdruck', 'waschanlage': 'Waschanlage', 'tiefdruck': 'Tiefdruck',
                        'klebstoffreiniger': 'Klebstoffreiniger', 'uv-offsetdruck': 'UV-Druck',
                        'klischeereiniger': 'Klischeereiniger', 'bodenreiniger': 'Bodenreiniger',
                        'entfetter': 'Entfetter', 'reflektorreiniger': 'Reflektorreiniger'}
        for i in usecasevocab:
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO usecases (usecase_name) VALUES ('%s');" % i)
            conn.commit()
            # print(manuell_title)  # correct
            cur.close()
            print("Added %s to usecases" % i)


        for i in erg6:
            import pdb; pdb.set_trace()
            datenblatt_title = i.get('title')
            datenblatt_desc = i.get('description')
            datenblatt_uid = get_webcode(self)
            datenblatt_link = i.get('@id')
            datenblatt_skin_category = i.get('hskategorie')
            datenblatt_checked_emissions = i.get('emissionsgeprueft')
            datenblatt_product_category = i.get('produktkategorie')
            datenblatt_product_class = i.get('produktklasse')
            datenblatt_flashpoint = i.get('flammpunkt')
            datenblatt_values_range = i.get('wertebereich')
            datenblatt_material_compatibility = i.get('materialvertraeglichkeit')
            datenblatt_comments = i.get('bemerkungen')
            datenblatt_review_state = i.get('review_state')
            datenblatt_manufacturer_name = i.get('hersteller')['title']

            if datenblatt_review_state == 'published':
                datenblatt_published = 'published'
            else:
                datenblatt_published = 'private'

            if datenblatt_skin_category:
                pass
            else:
                datenblatt_skin_category = ''

            if datenblatt_product_category:
                if datenblatt_product_category[0] == 'UV-Druck':
                    datenblatt_substancetype = 'uv'
                else:
                    datenblatt_substancetype = 'offset'
            else:
                datenblatt_substancetype = 'leer'

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(datenblatt_manufacturer_name))
            datenblatt_manufacturer_id = cur.fetchall()
            cur.close()

            if datenblatt_manufacturer_id:
                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, comments, status, manufacturer_id) VALUES (%s, %s, %s, 'druck_und_papier', %s, NULL, %s, %s, %s, %s, %s, %s, %s);",
                    (datenblatt_title, datenblatt_desc, datenblatt_uid, datenblatt_substancetype,
                     datenblatt_skin_category,
                     datenblatt_checked_emissions, datenblatt_flashpoint, datenblatt_values_range,
                     str(datenblatt_comments), datenblatt_published, datenblatt_manufacturer_id[0]))
                conn.commit()
                # print(datenblatt_title)  # correct
                cur.close()
            else:
                print("Keine ID")
                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, comments, status) VALUES (%s, %s, %s, 'druck_und_papier', %s, NULL, %s, %s, %s, %s, %s, %s);",
                    (datenblatt_title, datenblatt_desc, datenblatt_uid, datenblatt_substancetype, datenblatt_skin_category,
                     datenblatt_checked_emissions, datenblatt_flashpoint, datenblatt_values_range,
                     str(datenblatt_comments), datenblatt_published))
                conn.commit()
                # print(datenblatt_title)  # correct
                cur.close()

        print('Successfully migrated PRODUCT_DATASHEET')

        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')

        return template
