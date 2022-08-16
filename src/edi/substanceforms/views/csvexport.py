# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from edi.substanceforms.lib import DBConnect
from edi.substanceforms.helpers import get_vocabulary
import csv

class Csvmixture(BrowserView):

    def __call__(self):
        self.create_mixture_file()
        file = open('/tmp/mixtures.csv', 'rb')
        file.seek(0)
        filename = 'mixtures.csv'
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'text/csv')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' %filename)
        return file.read()

    def create_mixture_file(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username,
                            password=self.context.password)

        mixtureselect = "SELECT * FROM substance_mixture"
        mixtures = self.db.execute(mixtureselect)

        with open('/tmp/mixtures.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            writer.writerow(['ID', 'Titel', 'Beschreibung', 'Webcode', 'Branche', 'Typ des Gefahrstoffgemischs',
                                 'application_areas', 'usecases', 'Verdampfungsfaktor 150', 'Verdampfungsfaktor 160', 'Verdampfungsfaktor 170',
                                 'Verdampfungsfaktor 180', 'UEG', 'Responsefaktor', 'Hautschutzmittelkategorie',
                                 'Emissionsgeprüft', 'Prüfdatum', 'Flammpunkt', 'Wertebereich', 'Klassifikationen',
                                 'Indikatoren', 'Kommentare', 'Hersteller', 'Status', 'Produktklasse', 'Zusammensetung', 'CAS-Nummer Bestandteil', 'Konzentration Bestandteil'])


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

                if classifications:
                    newclassifications = classifications.split('@')
                else:
                    newclassifications = classifications

                if indicators:
                    newindicators = indicators.split('@')
                else:
                    newindicators = indicators

                applicationareas = []
                select = "SELECT area_id from areapairs WHERE mixture_id = %s" % id
                areaids = self.db.execute(select)

                for arid in areaids:
                    select = "SELECT application_area_name from application_areas WHERE application_area_id = %s" % arid
                    area_title = self.db.execute(select)
                    applicationareas.append(area_title)

                newapplicationareas = list()
                if applicationareas:
                    for i in applicationareas:
                        newapplicationareas.append(i[0][0])
                else:
                    newapplicationareas = "keine Angabe"

                usecases = []
                select = "SELECT usecase_id from usecasepairs WHERE mixture_id = %s" % id
                usecaseids = self.db.execute(select)

                for ucid in usecaseids:
                    select = "SELECT usecase_name from usecases WHERE usecase_id = %s" % ucid
                    usecase_title = self.db.execute(select)
                    usecases.append(usecase_title)

                newusecases = list()
                if usecases:
                    for i in usecases:
                        newusecases.append(i[0][0])
                else:
                    newusecases = "keine Angabe"

                newentries = list()
                number = 0
                with open(
                    '/home/bgetem/praevention/src/edi.substanceforms/src/edi/substanceforms/views/zusammensetzung.csv',
                    newline='') as csvfile2:
                    reader = csv.reader(csvfile2, delimiter=';', quotechar='"')
                    for row in reader:
                        entry = '€'.join(row)
                        newentries.append(entry)
                        print("Fetched SUBSTANCE NUMBER " + str(number))
                        number = number + 1


                zusammensetzung = "keine Angabe"
                for e in newentries:
                    zusammensetzungsresult = e.split('€')
                    if zusammensetzungsresult[0] == title:
                        zusammensetzung = list()
                        resu = zusammensetzungsresult[1]
                        result = resu.split('|')
                        for i in result:
                            zusammensetzung.append(i)


                if isinstance(zusammensetzung, list):
                    newzusammensetzung = zusammensetzung[0].split('@')
                    try:
                        if len(newzusammensetzung) == 1:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], None, None])
                        elif len(newzusammensetzung) == 2:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], newzusammensetzung[1], None])
                        else:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], newzusammensetzung[1], newzusammensetzung[2]])
                    except:
                        import pdb; pdb.set_trace()
                    if len(zusammensetzung) > 1:
                        zusammensetzung.pop(0)
                        for i in zusammensetzung:
                            newzusammensetzung = i.split('@')
                            if len(newzusammensetzung) == 1:
                                writer.writerow([None, None, None, None, None, None, None, None, None, None, None, None, None,
                                                 None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], None, None])
                            elif len(newzusammensetzung) == 2:
                                writer.writerow(
                                    [None, None, None, None, None, None, None, None, None, None, None, None, None,
                                     None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], newzusammensetzung[1], None])
                            else:
                                writer.writerow(
                                    [None, None, None, None, None, None, None, None, None, None, None, None, None,
                                     None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], newzusammensetzung[1], newzusammensetzung[2]])
                else:
                    writer.writerow(
                        [id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases,
                         evap_150, evap_160, evap_170, evap_180, ueg, response, newskincategory, newchecked_emissions,
                         date_checked, flashpoint, newvalues_range, newclassifications, newindicators, comments, manufacturer,
                         status, newproductclass, zusammensetzung, None, None])


        return None

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value


class CsvmixtureNew(BrowserView):

    def __call__(self):
        self.create_mixture_file()
        file = open('/tmp/mixturesnew.csv', 'rb')
        file.seek(0)
        filename = 'mixturesnew.csv'
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'text/csv')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' %filename)
        return file.read()

    def create_mixture_file(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username,
                            password=self.context.password)

        mixtureselect = "SELECT * FROM substance_mixture"
        mixtures = self.db.execute(mixtureselect)

        with open('/tmp/mixturesnew.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            writer.writerow(['ID', 'Titel', 'Beschreibung', 'Webcode', 'Branche', 'Typ des Gefahrstoffgemischs',
                                 'application_areas', 'usecases', 'Verdampfungsfaktor 150', 'Verdampfungsfaktor 160', 'Verdampfungsfaktor 170',
                                 'Verdampfungsfaktor 180', 'UEG', 'Responsefaktor', 'Hautschutzmittelkategorie',
                                 'Emissionsgeprüft', 'Prüfdatum', 'Flammpunkt', 'Wertebereich', 'Klassifikationen',
                                 'Indikatoren', 'Kommentare', 'Hersteller', 'Status', 'Produktklasse', 'Zusammensetung', 'CAS-Nummer Bestandteil', 'Konzentration Bestandteil'])


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

                if classifications:
                    newclassifications = classifications.split('@')
                else:
                    newclassifications = classifications

                if indicators:
                    newindicators = indicators.split('@')
                else:
                    newindicators = indicators

                applicationareas = []
                select = "SELECT area_id from areapairs WHERE mixture_id = %s" % id
                areaids = self.db.execute(select)

                for arid in areaids:
                    select = "SELECT application_area_name from application_areas WHERE application_area_id = %s" % arid
                    area_title = self.db.execute(select)
                    applicationareas.append(area_title)

                newapplicationareas = list()
                if applicationareas:
                    for i in applicationareas:
                        newapplicationareas.append(i[0][0])
                else:
                    newapplicationareas = "keine Angabe"

                usecases = []
                select = "SELECT usecase_id from usecasepairs WHERE mixture_id = %s" % id
                usecaseids = self.db.execute(select)

                for ucid in usecaseids:
                    select = "SELECT usecase_name from usecases WHERE usecase_id = %s" % ucid
                    usecase_title = self.db.execute(select)
                    usecases.append(usecase_title)

                newusecases = list()
                if usecases:
                    for i in usecases:
                        newusecases.append(i[0][0])
                else:
                    newusecases = "keine Angabe"

                import pdb; pdb.set_trace()

                zusammensetzungsselect = "SELECT * FROM recipes WHERE mixture_id = %s" % id
                newentries = self.db.execute(zusammensetzungsselect)


                zusammensetzung = "keine Angabe"
                for e in newentries:
                    zusammensetzungsresult = e.split('€')
                    if zusammensetzungsresult[0] == title:
                        zusammensetzung = list()
                        resu = zusammensetzungsresult[1]
                        result = resu.split('|')
                        for i in result:
                            zusammensetzung.append(i)


                if isinstance(zusammensetzung, list):
                    newzusammensetzung = zusammensetzung[0].split('@')
                    try:
                        if len(newzusammensetzung) == 1:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], None, None])
                        elif len(newzusammensetzung) == 2:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], newzusammensetzung[1], None])
                        else:
                            writer.writerow([id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases, evap_150, evap_160, evap_170, evap_180,
                                            ueg, response, newskincategory, newchecked_emissions, date_checked, flashpoint, newvalues_range,
                                            newclassifications, newindicators, comments, manufacturer, status, newproductclass, newzusammensetzung[0], newzusammensetzung[1], newzusammensetzung[2]])
                    except:
                        import pdb; pdb.set_trace()
                    if len(zusammensetzung) > 1:
                        zusammensetzung.pop(0)
                        for i in zusammensetzung:
                            newzusammensetzung = i.split('@')
                            if len(newzusammensetzung) == 1:
                                writer.writerow([None, None, None, None, None, None, None, None, None, None, None, None, None,
                                                 None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], None, None])
                            elif len(newzusammensetzung) == 2:
                                writer.writerow(
                                    [None, None, None, None, None, None, None, None, None, None, None, None, None,
                                     None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], newzusammensetzung[1], None])
                            else:
                                writer.writerow(
                                    [None, None, None, None, None, None, None, None, None, None, None, None, None,
                                     None, None, None, None, None, None, None, None, None, None, None, None, newzusammensetzung[0], newzusammensetzung[1], newzusammensetzung[2]])
                else:
                    writer.writerow(
                        [id, title, description, webcode, newbranch, newsubstancetype, newapplicationareas, newusecases,
                         evap_150, evap_160, evap_170, evap_180, ueg, response, newskincategory, newchecked_emissions,
                         date_checked, flashpoint, newvalues_range, newclassifications, newindicators, comments, manufacturer,
                         status, newproductclass, zusammensetzung, None, None])


        return None

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value

class Csvpowder(BrowserView):

    def __call__(self):
        self.create_powder_file()
        file = open('/tmp/powders.csv', 'rb')
        file.seek(0)
        filename = 'powders.csv'
        RESPONSE = self.request.response
        RESPONSE.setHeader('content-type', 'text/csv')
        RESPONSE.setHeader('content-disposition', 'attachment; filename=%s' %filename)
        return file.read()

    def create_powder_file(self):
        self.db = DBConnect(host=self.context.host, db=self.context.database, user=self.context.username,
                            password=self.context.password)

        powderselect = "SELECT * FROM spray_powder;"
        powders = self.db.execute(powderselect)

        with open('/tmp/powders.csv', 'w', newline='') as powdercsv:
            powderwriter = csv.writer(powdercsv, delimiter=';', quotechar='"')
            powderwriter.writerow(['ID', 'Titel', 'Beschreibung', 'Webcode', 'Produktklasse', 'Ausgangsmaterial', 'Medianwert',
                             'Volumenanteil', 'Emissionsgeprüft', 'Prüfdatum', 'Hersteller', 'Status'])

            for i in powders:
                powderid = i[0]
                powdertitle = i[1]
                powderdescription = i[2]
                powderwebcode = i[3]
                powderproductclass = i[4]
                powderstartingmaterial = i[5]
                powdermedian = i[6]
                powdervolumeshare = i[7]
                powdercheckedemissions = i[8]
                powderdatechecked = i[9]
                powdermanufacturerid = i[11]
                powderstatus = i[12]

                if powdermanufacturerid:
                    powdermanufacturer = (self.db.execute("SELECT title FROM manufacturer WHERE manufacturer_id = %s" % powdermanufacturerid))[0][0]
                else:
                    powdermanufacturer = 'keine Angabe'
                newpowdercheckedemissions = self.get_attr_translation('boolvocab', str(powdercheckedemissions))

                powderwriter.writerow(
                    [powderid, powdertitle, powderdescription, powderwebcode, powderproductclass, powderstartingmaterial,
                     powdermedian, powdervolumeshare, newpowdercheckedemissions, powderdatechecked, powdermanufacturer,
                     powderstatus])


        return None

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value
