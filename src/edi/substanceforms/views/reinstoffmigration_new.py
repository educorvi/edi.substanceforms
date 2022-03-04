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

        def getReinstoffe():
            newentries = list()
            number = 0
            with open('/home/plone_buildout/plone52/src/edi.substanceforms/src/edi/substanceforms/views/zvg-cas-list-d.csv', newline='') as csvfile:
                test = csv.reader(csvfile, delimiter=';', quotechar='"')
                for row in test:
                    entry = '@'.join(row)
                    newentries.append(entry)
                    print("Fetched SUBSTANCE NUMBER "+str(number))
                    number = number + 1
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

        erg1 = getReinstoffe()
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        zahl = 0
        for i in erg1:
            ergebnis = i.split('@')
            import pdb;pdb.set_trace()
            reinstoff_title = ergebnis[0]
            reinstoff_uid = get_webcode(self)
            reinstoff_casnr = ergebnis[3]
            reinstoff_egnr = ergebnis[4]
            reinstoff_lokal = ergebnis[5]
            reinstoff_systemisch = ergebnis[6]
            reinstoff_hinweise = ergebnis[10]
            reinstoff_link_id = ergebnis[11]
            reinstoff_link_available= ergebnis[12]
            reinstoff_skin = 'id_wechselnd'
            reinstoff_branche = 'alle_branchen'
            reinstoff_published = 'published'

            if reinstoff_link_available == "zum Stoff":
                reinstoff_link = "https://gestis.dguv.de/data?name="+str(reinstoff_link_id)
                cur = conn.cursor()

                cur.execute(
                    "INSERT INTO substance (title, webcode, casnr, egnr, skin_category, branch, dnel_lokal, dnel_systemisch, comments, link, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (reinstoff_title, reinstoff_uid, reinstoff_casnr, reinstoff_egnr, reinstoff_skin, reinstoff_branche, reinstoff_lokal,
                     reinstoff_systemisch, reinstoff_hinweise, reinstoff_link, reinstoff_published))
            else:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO substance (title, webcode, casnr, egnr, skin_category, branch, dnel_lokal, dnel_systemisch, comments, link, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s);",
                    (reinstoff_title, reinstoff_uid, reinstoff_casnr, reinstoff_egnr, reinstoff_skin,
                     reinstoff_branche, reinstoff_lokal,
                     reinstoff_systemisch, reinstoff_hinweise, reinstoff_published))
            conn.commit()
            cur.close()

            print('Successfully migrated SUBSTANCE '+str(zahl)+' '+reinstoff_title)
            zahl = zahl + 1

        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')

        return template
