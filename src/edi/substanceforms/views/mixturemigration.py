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

        usecasevocab = [['buchdruck', 'Buchdruck'], ['flexodruck', 'Flexodruck'], ['siebdruck', 'Siebdruck'],
                        ['farbreiniger_alle_druckverfahren', 'Farbreiniger alle Druckverfahren'],
                        ['offsetdruck', 'Offsetdruck'], ['waschanlage', 'Waschanlage'], ['tiefdruck', 'Tiefdruck'],
                        ['klebstoffreiniger', 'Klebstoffreiniger'], ['uv-offsetdruck', 'UV-Druck'],
                        ['klischeereiniger', 'Klischeereiniger'], ['bodenreiniger', 'Bodenreiniger'],
                        ['entfetter', 'Entfetter'], ['reflektorreiniger', 'Reflektorreiniger']]
        for i in usecasevocab:
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO usecases (usecase_name, usecase_realname) VALUES (%s, %s);",(i[0], i[1]))
            conn.commit()
            # print(manuell_title)  # correct
            cur.close()
            print("Added %s to usecases" % i)

        for i in erg4:
            etikett_title = i.get('title')
            etikett_desc = i.get('description')
            etikett_uid = get_webcode(self)
            etikett_skin_category = i.get('hskategorie')
            etikett_checked_emissions = i.get('emissionsgeprueft')
            etikett_flashpoint = i.get('flammpunkt')
            etikett_values_range = i.get('wertebereich')
            etikett_classifications = i.get('einstufung')
            etikett_hinweise = i.get('saetze')
            etikett_usecases = i.get('verwendungszweck')
            etikett_review_state = i.get('review_state')

            #if etikett_usecases:
            #    usecases_string = '@'.join(etikett_usecases)
            #    etikett_usecases = usecases_string

            if etikett_classifications:
                if etikett_classifications != []:
                    classifications_string = '@'.join(etikett_classifications)
                else:
                    classifications_string = ''
            else:
                classifications_string = ''

            etikett_classifications = classifications_string

            if etikett_hinweise:
                hinweise_string = '@'.join(etikett_hinweise)
                etikett_hinweise = hinweise_string

            if etikett_review_state == 'published':
                etikett_published = 'published'
            else:
                etikett_published = 'private'

            if i.get('hersteller'):
                etikett_manufacturer_name = i.get('hersteller')['title']
                cur = conn.cursor()
                cur.execute(
                    "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(etikett_manufacturer_name))
                etikett_manufacturer_id = cur.fetchall()
                cur.close()

                if etikett_manufacturer_id != []:
                    cur = conn.cursor()
                    # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                    cur.execute(
                        "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, manufacturer_id, status, classifications, indicators) VALUES (%s, %s, %s, 'druck_und_papier', 'label', NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (etikett_title, etikett_desc, etikett_uid, etikett_skin_category, etikett_checked_emissions,
                         etikett_flashpoint, etikett_values_range, etikett_usecases, etikett_manufacturer_id[0], etikett_published, etikett_classifications, etikett_hinweise))
                    conn.commit()
                    # print(etikett_title)  # correct
                    cur.close()
                else:
                    cur = conn.cursor()
                    # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                    cur.execute(
                        "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, status, classifications, indicators) VALUES (%s, %s, %s, 'druck_und_papier', 'label', NULL, %s, %s, %s, %s, %s, %s, %s, %s);",
                        (etikett_title, etikett_desc, etikett_uid, etikett_skin_category, etikett_checked_emissions,
                         etikett_flashpoint, etikett_values_range, etikett_usecases, etikett_published, etikett_classifications, etikett_hinweise))
                    conn.commit()
                    # print(etikett_title)  # correct
                    cur.close()

            else:
                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, status, classifications, indicators) VALUES (%s, %s, %s, 'druck_und_papier', 'label', NULL, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (etikett_title, etikett_desc, etikett_uid, etikett_skin_category, etikett_checked_emissions,
                     etikett_flashpoint, etikett_values_range, etikett_usecases, etikett_published, etikett_classifications, etikett_hinweise))
                conn.commit()
                # print(etikett_title)  # correct
                cur.close()

            if etikett_usecases:
                for i in etikett_usecases:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT usecase_id FROM usecases WHERE usecase_name = '{0}';".format(i))
                    usecaseid = cur.fetchall()
                    cur.close()

                    cur = conn.cursor()
                    cur.execute(
                        "SELECT substance_mixture_id FROM substance_mixture ORDER BY substance_mixture_id DESC LIMIT 1;")
                    mixtureid = cur.fetchall()
                    cur.close()

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO usecasepairs (usecase_id, mixture_id) VALUES (%s, %s);",
                        (usecaseid[0][0], mixtureid[0][0]))
                    conn.commit()
                    # print(manuell_title)  # correct
                    cur.close()

        print('Successfully migrated DETERGENT_LABELS')

        areavocab = ['Farbreiniger', 'Plattenreiniger', 'Feuchtwalzenreiniger', 'Gummituchregenerierer',
                     'Reiniger für Leitstände, Sensoren', 'Klebstoffreiniger']
        for i in areavocab:
            cur = conn.cursor()
            # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
            cur.execute(
                "INSERT INTO application_areas (application_area_name) VALUES ('%s');" % i)
            conn.commit()
            # print(manuell_title)  # correct
            cur.close()
            print("Added %s to application_areas" %i)

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
            manuell_review_state = i.get('review_state')

            if manuell_usecases:
                print ("TESTTESTTESTTESTTESTTEST")
                #usecases_string = '@'.join(manuell_usecases)
                #manuell_usecases = usecases_string

                #areas_string = '@'.join(manuell_application_areas)
                #manuell_application_areas = areas_string

            if manuell_review_state == 'published':
                manuell_published = 'published'
            else:
                manuell_published = 'private'

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(manuell_manufacturer_name))
            manuell_manufacturer_id = cur.fetchall()
            cur.close()
            if manuell_manufacturer_id:
                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, application_areas, manufacturer_id, status) VALUES (%s, %s, %s, 'druck_und_papier', 'special', NULL, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (manuell_title, manuell_desc, manuell_uid, manuell_skin_category, manuell_checked_emissions,
                     manuell_flashpoint, manuell_values_range, manuell_usecases, manuell_application_areas,
                     manuell_manufacturer_id[0], manuell_published))
                conn.commit()
                # print(manuell_title)  # correct
                cur.close()
            else:
                cur = conn.cursor()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, skin_category, checked_emissions, flashpoint, values_range, usecases, application_areas, manufacturer_id, status) VALUES (%s, %s, %s, 'druck_und_papier', 'special', NULL, %s, %s, %s, %s, %s, %s, NULL, %s);",
                    (manuell_title, manuell_desc, manuell_uid, manuell_skin_category, manuell_checked_emissions,
                     manuell_flashpoint, manuell_values_range, manuell_usecases, manuell_application_areas,
                     manuell_published))
                conn.commit()
                # print(manuell_title)  # correct
                cur.close()

            if manuell_application_areas:
                for i in manuell_application_areas:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT application_area_id FROM application_areas WHERE application_area_name = '{0}';".format(i))
                    areaid = cur.fetchall()
                    cur.close()

                    cur = conn.cursor()
                    cur.execute(
                        "SELECT substance_mixture_id FROM substance_mixture ORDER BY substance_mixture_id DESC LIMIT 1;")
                    mixtureid = cur.fetchall()
                    cur.close()

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO areapairs (area_id, mixture_id) VALUES (%s, %s);",
                        (areaid[0][0], mixtureid[0][0]))
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
            heatset_review_state = i.get('review_state')
            heatset_verdampfung = i.get('verdampfung')
            heatset_manufacturer_name = i.get('hersteller')['title']

            heatset_evap_150 = heatset_verdampfung[0].get('bahn_150')
            heatset_evap_160 = heatset_verdampfung[0].get('bahn_160')
            heatset_evap_170 = heatset_verdampfung[0].get('bahn_170')
            heatset_evap_180 = heatset_verdampfung[0].get('bahn_180')

            if heatset_review_state == 'published':
                heatset_published = 'published'
            else:
                heatset_published = 'private'

            if heatset_skin_category:
                pass
            else:
                heatset_skin_category = ''

            cur = conn.cursor()
            cur.execute(
                "SELECT manufacturer_id FROM manufacturer WHERE title = '{0}';".format(heatset_manufacturer_name))
            heatset_manufacturer_id = cur.fetchall()
            cur.close()

            if heatset_manufacturer_id:
                cur = conn.cursor()
                # import pdb; pdb.set_trace()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, ueg, response, skin_category, date_checked, checked_emissions, evaporation_lane_150, evaporation_lane_160, evaporation_lane_170, evaporation_lane_180, manufacturer_id, status) VALUES (%s, %s, %s, 'druck_und_papier', 'heatset', NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (heatset_title, heatset_desc, heatset_uid, heatset_ueg, heatset_response, heatset_skin_category,
                     heatset_date_checked, heatset_checked_emissions, heatset_evap_150, heatset_evap_160, heatset_evap_170, heatset_evap_180, heatset_manufacturer_id[0], heatset_published ))
                conn.commit()
                # print(heatset_title)  # correct
                cur.close()
            else:
                print("Keine Heatset ID")
                cur = conn.cursor()
                # import pdb; pdb.set_trace()
                # cur.execute("INSERT INTO manufacturer (title, description, webcode) VALUES (%s, %s, %s)") % (hersteller_title, hersteller_desc, hersteller_uid)
                cur.execute(
                    "INSERT INTO substance_mixture (title, description, webcode, branch, substance_type, image_url, ueg, response, skin_category, date_checked, checked_emissions, evaporation_lane_150, evaporation_lane_160, evaporation_lane_170, evaporation_lane_180, status) VALUES (%s, %s, %s, 'druck_und_papier', 'heatset', NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (heatset_title, heatset_desc, heatset_uid, heatset_ueg, heatset_response, heatset_skin_category,
                     heatset_date_checked, heatset_checked_emissions, heatset_evap_150, heatset_evap_160,
                     heatset_evap_170, heatset_evap_180, heatset_published))
                conn.commit()
                # print(heatset_title)  # correct
                cur.close()

        print('Successfully migrated DETERGENT_HEATSET')
        print('CHEERS! DATA MIGRATION SUCCESSFULLY COMPLETED :)')


        return template
