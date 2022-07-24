# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from edi.substanceforms.lib import DBConnect
from edi.substanceforms.helpers import get_vocabulary
import csv


class Csvexport(BrowserView):
    def __call__(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username,
                            password=self.context.password)
        template = '''<li class="heading" i18n:translate="">
          Sample View
        </li>'''

        mixtureselect = "SELECT * FROM substance_mixture"
        mixtures = self.db.execute(mixtureselect)

        with open('/home/plone_buildout/praevention/src/edi.substanceforms/src/edi/substanceforms/views/test.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            writer.writerow(['ID', 'Titel', 'Beschreibung', 'Webcode', 'Branche', 'Typ des Gefahrstoffgemischs',
                                 'application_areas', 'Verdampfungsfaktor 150', 'Verdampfungsfaktor 160', 'Verdampfungsfaktor 170',
                                 'Verdampfungsfaktor 180', 'UEG', 'Responsefaktor', 'Hautschutzmittelkategorie',
                                 'Emissionsgeprüft', 'Prüfdatum', 'Flammpunkt', 'Wertebereich', 'Klassifikationen',
                                 'Indikatoren', 'Kommentare', 'Hersteller', 'Status', 'Produktklasse'])


            for i in mixtures:
                id = i[0]
                title = i[1]
                description = i[2]
                webcode = i[3]
                branch = i[4]
                substance_type = i[5]
                evap_150 = i[10]
                evap_160 = i[11]
                evap_170 = i[12]
                evap_180 = i[13]
                ueg = i[14]
                response = i[15]
                skin_category = i[16]
                checked_emissions = i[17]
                date_checked = i[18]
                flashpoint = i[19]
                values_range = i[20]
                classifications = i[21]
                indicators = i[22]
                comments = i[23]
                manufacturer_id = i[25]
                status = i[26]
                productclass = i[27]

                if manufacturer_id:
                    manufacturer = (self.db.execute("SELECT title FROM manufacturer WHERE manufacturer_id = %s" % manufacturer_id))[0][0]
                else:
                    manufacturer = 'keine Angabe'
                newbranch = self.get_attr_translation('branch', branch)
                newsubstancetype = self.get_attr_translation('substance_type', substance_type)
                newskincategory = self.get_attr_translation('hskategorie', skin_category)
                newchecked_emissions = self.get_attr_translation('boolvocab', str(checked_emissions))
                newvalues_range = self.get_attr_translation('boolvocab', str(values_range))
                if productclass:
                    newproductclass = (self.db.execute("SELECT class_name FROM productclasses WHERE class_id = %s" % productclass))[0][0]
                else:
                    newproductclass = 'keine Angabe'

                applicationareas = []
                select = "SELECT area_id from areapairs WHERE mixture_id = %s" % id
                areaids = self.db.execute(select)

                for arid in areaids:
                    select = "SELECT application_area_name from application_areas WHERE application_area_id = %s" % arid
                    area_title = self.db.execute(select)
                    applicationareas.append(area_title)

                if applicationareas:
                    newapplicationareas = applicationareas[0][0]
                else:
                    newapplicationareas = "keine Angabe"


                writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, evap_150, evap_160, evap_170, evap_180,
                                ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                classifications, indicators, comments, manufacturer, status, newproductclass])

                #import pdb; pdb.set_trace()


        return template

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value
