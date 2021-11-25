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
                cur = conn.cursor()
                select = "SELECT webcode from %s WHERE webcode = '%s'" % (table, generated_webcode)
                try:
                    cur.execute(select)
                    erg = cur.fetchall()
                except:
                    erg = False
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
            hersteller_uid = get_webcode(self)
            hersteller_homepage = i.get('homepage')
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute("INSERT INTO manufacturer (title, description, webcode, homepage) VALUES (%s, %s, %s, %s);",
                        (hersteller_title, hersteller_desc, hersteller_uid, hersteller_homepage))
            conn.commit()
            # print(hersteller_title)# correct
            cur.close()

        print('Successfully migrated MANUFACTURER')

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

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(powder_manufacturer_name))
            powder_manufacturer_id = cur.fetchall()
            cur.close()

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO spray_powder (title, description, webcode, manufacturer_id, image_url, product_class, starting_material, median_value, volume_share, checked_emissions, date_checked) VALUES (%s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s);",
                (powder_title, powder_desc, powder_uid, powder_manufacturer_id[0], powder_product_class,
                 powder_starting_material, powder_median_value, powder_volume_share, powder_checked_emissions,
                 powder_date_checked))
            conn.commit()
            cur.close()

        print('Successfully migrated SPRAY_POWDER')

        for i in erg4:
            etikett_title = i.get('title')
            etikett_desc = i.get('description')
            etikett_uid = get_webcode(self)
            etikett_skin_category = i.get('hskategorie')
            etikett_checked_emissions = i.get('emissionsgeprueft')
            etikett_flashpoint = i.get('flammpunkt')
            etikett_values_range = i.get('wertebereich')
            etikett_classifications = i.get('einstufungen')
            etikett_usecases = i.get('verwendungszweck')
            etikett_manufacturer_name = i.get('hersteller')['title']

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(etikett_manufacturer_name))
            etikett_manufacturer_id = cur.fetchall()
            cur.close()

            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, manufacturer_id) VALUES (%s, %s, %s, 'branch', 'label', NULL, %s, %s, %s, %s, %s, %s);",
                (etikett_title, etikett_desc, etikett_uid, etikett_skin_category, etikett_checked_emissions,
                 etikett_flashpoint, etikett_values_range, etikett_usecases, etikett_manufacturer_id[0]))
            conn.commit()
            # print(etikett_title)  # correct
            cur.close()

        print('Successfully migrated DETERGENT_LABELS')

        for i in erg5:
            manuell_title = i.get('title')
            manuell_desc = i.get('description')
            manuell_uid = get_webcode(self)
            manuell_link = i.get('@id')
            manuell_skin_category = i.get('hskategorie')
            manuell_checked_emissions = i.get('emissionsgeprueft')
            manuell_flashpoint = i.get('flammpunkt')
            manuell_values_range = i.get('wertebereich')
            manuell_usecases = i.get('verwendungszweck')
            manuell_application_areas = i.get('anwendungsgebiete')
            manuell_manufacturer_name = i.get('hersteller')['title']

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(manuell_manufacturer_name))
            manuell_manufacturer_id = cur.fetchall()
            cur.close()

            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, application_areas, manufacturer_id) VALUES (%s, %s, %s, 'branch', 'offset', NULL, %s, %s, %s, %s, %s, %s, %s);",
                (manuell_title, manuell_desc, manuell_uid, manuell_skin_category, manuell_checked_emissions,
                 manuell_flashpoint, manuell_values_range, manuell_usecases, manuell_application_areas,
                 manuell_manufacturer_id[0]))
            conn.commit()
            # print(manuell_title)  # correct
            cur.close()

        print('Successfully migrated DETERGENT_MANUAL')

        for i in erg6:
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

            if datenblatt_skin_category:
                pass
            else:
                datenblatt_skin_category = ''

            try:
                if datenblatt_product_category[0] == 'Konventionell':
                    offsetprintmanner = 'without_spec'
                elif datenblatt_product_category[0] == 'UV-Druck':
                    offsetprintmanner = 'uv_print'
                else:
                    offsetprintmanner = 'without_spec'
            except:
                offsetprintmanner = 'without_spec'

            # import pdb; pdb.set_trace()
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, comments, offset_print_manner) VALUES (%s, %s, %s, 'branch', 'offset', NULL, %s, %s, %s, %s, %s, %s);",
                (datenblatt_title, datenblatt_desc, datenblatt_uid, datenblatt_skin_category,
                 datenblatt_checked_emissions, datenblatt_flashpoint, datenblatt_values_range,
                 str(datenblatt_comments),offsetprintmanner))
            conn.commit()
            # print(datenblatt_title)  # correct
            cur.close()

        print('Successfully migrated PRODUCT_DATASHEET')

        for i in erg7:
            heatset_title = i.get('title')
            heatset_desc = i.get('description')
            heatset_uid = get_webcode(self)
            heatset_link = i.get('@id')
            heatset_ueg = i.get('ueg')
            heatset_response = i.get('response')
            heatset_skin_category = i.get('hskategorie')
            heatset_date_checked = i.get('pruefdateum')
            heatset_checked_emissions = i.get('emissionsgeprueft')

            if heatset_skin_category:
                pass
            else:
                heatset_skin_category = ''

            cur = conn.cursor()
            # import pdb; pdb.set_trace()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, ueg, response, skin_category, date_checked, checked_emissions) VALUES (%s, %s, %s, 'branch', 'offset', NULL, %s, %s, %s, %s, %s);",
                (heatset_title, heatset_desc, heatset_uid, heatset_ueg, heatset_response, heatset_skin_category,
                 heatset_date_checked, heatset_checked_emissions))
            conn.commit()
            # print(heatset_title)  # correct
            cur.close()

        print('Successfully migrated DETERGENT_HEATSET')
        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')


        return template
