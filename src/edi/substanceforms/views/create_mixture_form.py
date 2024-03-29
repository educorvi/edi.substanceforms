# -*- coding: utf-8 -*-

import transaction
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField, HiddenField
from plone.namedfile import NamedBlobImage
from wtforms import RadioField, SelectMultipleField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value, int_checker, list_handler, reverse_list_handler, new_list_handler, get_vocabulary, new_list_handler2, new_list_handler3
from edi.substanceforms.vocabularies import substance_types, hskategorie, produktkategorien, produktklassen, branchen
from edi.substanceforms.vocabularies import classifications, usecases, application_areas, substance_types_new, produktklassenid
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import re

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class CreateForm(Form):

    title = StringField(u"Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField(u"Beschreibung", render_kw={'class': 'form-control'})
    branch = RadioField("Branche", [validators.required()], choices=branchen)
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()], render_kw={'class': 'form-control edi-select'})
    substance_type = RadioField(u"Art des Wasch- und Reinigungsmittels", [validators.required()], choices=substance_types_new)
    usecases = MultiCheckboxField(u"Anwendungszwecke für Etikettenreiniger", choices=usecases)
    application_areas = MultiCheckboxField(u"Anwendungsgebiete für Sonderreiniger", choices=application_areas)
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 150 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 160 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 170 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 180 °C)", render_kw={'class': 'form-control'})
    productclass = RadioField("Produktklasse", [validators.required()], choices=produktklassenid)
    ueg = StringField(u"UEG in g/m3", render_kw={'class': 'form-control'})
    response = StringField(u"Response-Faktor", render_kw={'class': 'form-control'})
    skin_category = RadioField(u"Hautschutz-Kategorie", [validators.required()], choices=hskategorie)
    date_checked = DateField(u"Datum der letzten Prüfung", render_kw={'class': 'form-control', 'type': 'date'})
    checked_emissions = BooleanField(u"Emissionsarmes Produkt", render_kw={'class': 'form-check-input'})
    flashpoint = IntegerField(u"Flammpunkt [°C]", render_kw={'class': 'form-control'})
    values_range = BooleanField(u"Wertebereich", render_kw={'class': 'form-check-input'})
    image_url = FileField("Bilddatei hochladen", render_kw={'class': 'form-control'})
    comments = TextAreaField("Bemerkungen", render_kw={'class': 'form-control'})
    status = "published"

class UpdateForm(Form):

    title = StringField(u"Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField(u"Beschreibung", render_kw={'class': 'form-control'})
    branch = RadioField("Branche", choices=branchen)
    substance_type = RadioField(u"Art des Wasch- und Reinigungsmittels", [validators.required()], choices=substance_types_new)
    usecases = MultiCheckboxField(u"Anwendungszwecke für Etikettenreiniger", choices=usecases)
    application_areas = MultiCheckboxField(u"Anwendungsgebiete für Sonderreiniger", choices=application_areas)
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 150 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 160 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 170 °C)", render_kw={'class': 'form-control'})
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor Fv (Bahntemperatur 180 °C)", render_kw={'class': 'form-control'})
    productclass = RadioField("Produktklasse", [validators.required()], choices=produktklassenid)
    ueg = StringField(u"UEG in g/m3", render_kw={'class': 'form-control'})
    response = StringField(u"Response-Faktor", render_kw={'class': 'form-control'})
    skin_category = RadioField(u"Hautschutz-Kategorie", choices=hskategorie)
    date_checked = DateField(u"Datum der letzten Prüfung", render_kw={'class': 'form-control', 'type': 'date'})
    checked_emissions = BooleanField(u"Emissionsarmes Produkt", render_kw={'class': 'form-check-input'})
    flashpoint = IntegerField(u"Flammpunkt [°C]", render_kw={'class': 'form-control'})
    values_range = BooleanField(u"Wertebereich", render_kw={'class': 'form-check-input'})
    image_url = FileField("Bilddatei hochladen", render_kw={'class': 'form-control'})
    comments = TextAreaField("Bemerkungen", render_kw={'class': 'form-control'})
    no_image = BooleanField("Vorhandenes Bild entfernen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

class DeleteForm(Form):
    sure = BooleanField("Gefahrstoffgemisch löschen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

class DeleteIngredientsForm(Form):
    ingres = MultiCheckboxField(u"Bitte wählen Sie die Bestandteile aus, die Sie löschen möchten", choices=[])
    item_id = HiddenField()

class UpdateManufacturerForm(Form):
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()], render_kw={'class': 'form-control edi-select'})
    item_id = HiddenField()

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        return self.index()

    def renderForm(self):
        self.db.connect()
        select = "SELECT manufacturer_id, title FROM manufacturer ORDER BY title;"
        erg = self.db.execute(select)
        self.db.close()
        if erg:
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
        else:
            manus = []
        self.form.manufacturer_id.choices = manus
        self.form.process()
        return self.formTemplate()

    def create_image(self, image, title):
        filedata = image.data.read()
        filename = image.data.filename
        blobimage = NamedBlobImage(data=filedata, filename=filename)
        obj = ploneapi.content.create(type='Image', title=title, image=blobimage, container=self.context)
        obj.indexObject()
        transaction.commit()
        return obj.UID()

    def submit(self, button):
        self.db.connect()
        image_url = ''
        if self.form.image_url.data.filename:
            image_url = self.create_image(self.form.image_url, self.form.title.data)
        redirect_url = self.context.absolute_url()
        if button == 'Speichern':
            if not self.form.skin_category.data:
                message = u'Bitte füllen Sie das Feld "Hautschutz-Kategorie" aus'
                ploneapi.portal.show_message(message=message, type='error', request=self.request)
                return None
            if self.form.date_checked.data:
                date_checked = self.form.date_checked.data.strftime("%Y-%m-%d")
            else:
                date_checked = ''
            insert = """INSERT INTO substance_mixture (title, description, webcode, branch, substance_type,
                                                        evaporation_lane_150, evaporation_lane_160,
                                                        evaporation_lane_170, evaporation_lane_180, ueg, response,
                                                        skin_category, checked_emissions, date_checked, flashpoint,
                                                        values_range, comments, image_url, manufacturer_id, status, productclass)
                                                        VALUES ('%s', '%s', '%s', %s, '%s',
                                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                                        %s, %s, %s, %s);""" \
                                                        % (self.form.title.data,
                                                        self.form.description.data,
                                                        self.context.aq_parent.get_webcode(),
                                                        check_value(self.form.branch.data),
                                                        self.form.substance_type.data,
                                                        int_checker(self.form.evaporation_lane_150.data),
                                                        int_checker(self.form.evaporation_lane_160.data),
                                                        int_checker(self.form.evaporation_lane_170.data),
                                                        int_checker(self.form.evaporation_lane_180.data),
                                                        check_value(self.form.ueg.data),
                                                        check_value(self.form.response.data),
                                                        check_value(self.form.skin_category.data),
                                                        self.form.checked_emissions.data,
                                                        check_value(date_checked),
                                                        check_value(self.form.flashpoint.data),
                                                        self.form.values_range.data,
                                                        check_value(self.form.comments.data),
                                                        check_value(image_url),
                                                        check_value(self.form.manufacturer_id.data.split('ID:')[-1]),
                                                        check_value(self.form.status),
                                                        check_value(self.form.productclass.data))
            self.db.execute(insert)
            areaids = list()
            for i in self.form.application_areas.data:
                selectcommand = "SELECT substance_mixture_id FROM substance_mixture ORDER BY substance_mixture_id DESC LIMIT 1"
                selectedid = self.db.execute(selectcommand)
                areaids.append([int(i), (int(selectedid[0][0]))])
            caseids = list()
            for i in self.form.usecases.data:
                selectcommand = "SELECT substance_mixture_id FROM substance_mixture ORDER BY substance_mixture_id DESC LIMIT 1"
                selectedid = self.db.execute(selectcommand)
                caseids.append([int(i), (int(selectedid[0][0]))])
            for i in areaids:
                insertcommand = "INSERT INTO areapairs (area_id, mixture_id) VALUES (%s, %s)" % (i[0], i[1])
                self.db.execute(insertcommand)
            for i in caseids:
                insertcommand = "INSERT INTO usecasepairs (usecase_id, mixture_id) VALUES (%s, %s)" % (i[0], i[1])
                self.db.execute(insertcommand)
            message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)


class UpdateFormView(CreateFormView):
    formClass = UpdateForm

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        getter = """SELECT title, description, branch, substance_type,
                    application_areas, usecases, evaporation_lane_150, evaporation_lane_160, evaporation_lane_170,
                    evaporation_lane_180, ueg, response, skin_category, checked_emissions, date_checked, flashpoint,
                    values_range, comments, image_url, productclass
                    FROM %s WHERE %s_id = %s;""" % (self.context.tablename,
                                                    self.context.tablename,
                                                    self.itemid)

        relationalgetter = "SELECT application_areas.application_area_name FROM application_areas, areapairs WHERE areapairs.mixture_id = %s and areapairs.area_id = application_areas.application_area_id ;" % self.itemid
        relationalgetter2 = "SELECT usecases.usecase_name FROM usecases, usecasepairs WHERE usecasepairs.mixture_id = %s and usecasepairs.usecase_id = usecases.usecase_id ;" % self.itemid
        self.db.connect()
        self.result = self.db.execute(getter)
        self.relational = self.db.execute(relationalgetter)
        self.relational2 = self.db.execute(relationalgetter2)
        self.db.close()
        return self.index()

    def renderForm(self):
        self.form.title.default=self.result[0][0]
        self.form.description.default=self.result[0][1]
        self.form.branch.default = self.result[0][2]
        self.form.substance_type.default = self.result[0][3]
        self.form.application_areas.default = new_list_handler2(self.relational)
        self.form.usecases.default = new_list_handler3(self.relational2)
        self.form.evaporation_lane_150.default = self.result[0][6]
        self.form.evaporation_lane_160.default = self.result[0][7]
        self.form.evaporation_lane_170.default = self.result[0][8]
        self.form.evaporation_lane_180.default = self.result[0][9]
        self.form.productclass.default = self.result[0][19]
        self.form.ueg.default = self.result[0][10]
        self.form.response.default = self.result[0][11]
        self.form.skin_category.default = self.result[0][12]
        self.form.checked_emissions.default = self.result[0][13]
        self.form.date_checked.default = self.result[0][14]
        self.form.flashpoint.default = self.result[0][15]
        self.form.values_range.default = self.result[0][16]
        self.form.comments.default = self.result[0][17]
        self.form.image_url.default = self.result[0][18]
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern':
            if self.form.date_checked.data:
                date_checked = self.form.date_checked.data.strftime("%Y-%m-%d")
            else:
                date_checked = ''

            command = """UPDATE substance_mixture SET title=%s, description=%s, branch=%s, substance_type=%s,
                         evaporation_lane_150=%s, evaporation_lane_160=%s, evaporation_lane_170=%s, evaporation_lane_180=%s,
                         ueg=%s, response=%s, skin_category=%s, checked_emissions=%s,
                         flashpoint=%s, values_range=%s, comments=%s, productclass=%s, date_checked=%s
                         WHERE substance_mixture_id = %s;""" % \
                                                        (check_value(self.form.title.data),
                                                        check_value(self.form.description.data),
                                                        check_value(self.form.branch.data),
                                                        check_value(self.form.substance_type.data),
                                                        int_checker(self.form.evaporation_lane_150.data),
                                                        int_checker(self.form.evaporation_lane_160.data),
                                                        int_checker(self.form.evaporation_lane_170.data),
                                                        int_checker(self.form.evaporation_lane_180.data),
                                                        check_value(self.form.ueg.data),
                                                        check_value(self.form.response.data),
                                                        check_value(self.form.skin_category.data),
                                                        check_value(self.form.checked_emissions.data),
                                                        check_value(self.form.flashpoint.data),
                                                        check_value(self.form.values_range.data),
                                                        check_value(self.form.comments.data),
                                                        check_value(self.form.productclass.data),
                                                        check_value(date_checked),
                                                        check_value(self.form.item_id.data))

            self.db.execute(command)
            deletecommand = "DELETE FROM areapairs WHERE mixture_id = %s" % self.form.item_id.data
            self.db.execute(deletecommand)
            for i in self.form.application_areas.data:
                insertcommand = "INSERT INTO areapairs (area_id, mixture_id) VALUES (%s, %s)" % (int(i), self.form.item_id.data)
                self.db.execute(insertcommand)

            deletecommand2 = "DELETE FROM usecasepairs WHERE mixture_id = %s" % self.form.item_id.data
            self.db.execute(deletecommand2)
            for i in self.form.usecases.data:
                insertcommand2 = "INSERT INTO usecasepairs (usecase_id, mixture_id) VALUES (%s, %s)" % (
                int(i), self.form.item_id.data)
                self.db.execute(insertcommand2)

            message = u'Das Gefahrstoffgemisch wurde erfolgreich aktualisiert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class DeleteFormView(CreateFormView):
    formClass = DeleteForm

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        return self.index()


    def renderForm(self):
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url()
        if button == 'Speichern' and self.form.sure.data is True: #and self.validate():
            command = "DELETE FROM substance_mixture WHERE substance_mixture_id = %s" % (self.form.item_id.data)
            self.db.execute(command)
            deletecommand = "DELETE FROM areapairs WHERE mixture_id = %s" % self.form.item_id.data
            self.db.execute(deletecommand)
            deletecommand2 = "DELETE FROM usecasepairs WHERE mixture_id = %s" % self.form.item_id.data
            self.db.execute(deletecommand2)
            message = u'Das Gefahrstoffgemisch wurde erfolgreich gelöscht'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Speichern' and self.form.sure.data is False:
            message = u'Das Gefahrstoffgemisch wurde nicht gelöscht, da das Bestätigungsfeld nicht ausgewählt war.'
            ploneapi.portal.show_message(message=message, type='error', request=self.request)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class DeleteIngredientsFormView(CreateFormView):
    formClass = DeleteIngredientsForm
    buttons = ('Löschen', 'Abbrechen')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        return self.index()

    def alreadyselected(self):
        self.db.connect()
        newresult = list()
        itemid = self.request.get('itemid')
        select = "SELECT DISTINCT substance.substance_id, substance.title FROM substance, recipes, substance_mixture WHERE recipes.mixture_id = %s AND substance.substance_id = recipes.substance_id" % itemid
        result = self.db.execute(select)
        for i in result:
            newresult.append(i)
        self.db.close()
        return newresult

    def renderForm(self):
        self.form.item_id.default=self.itemid
        bestandteile = self.alreadyselected()
        optionlist = list()
        if bestandteile:
            for i in bestandteile:
                optionlist.append(i)
            self.form.ingres.choices = optionlist
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Löschen':
            if self.form.ingres.data:
                for i in self.form.ingres.data:
                    command = "DELETE FROM recipes WHERE mixture_id = %s AND substance_id = %s" % (self.form.item_id.data, i)
                    self.db.execute(command)
                message = u'Die Bestandteile wurden erfolgreich gelöscht'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)
                self.db.close()
                return self.request.response.redirect(redirect_url)
            else:
                message = u'Die Bestandteile wurden nicht gelöscht, da das Bestätigungsfeld nicht ausgewählt war.'
                ploneapi.portal.show_message(message=message, type='error', request=self.request)
                return self.request.response.redirect(redirect_url)
        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)


class UpdateManufacturerFormView(CreateFormView):
    formClass = UpdateManufacturerForm

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        return self.index()

    def renderForm(self):
        self.db.connect()
        insert = "SELECT manufacturer_id, title FROM manufacturer ORDER BY title;"
        erg = self.db.execute(insert)
        manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
        self.form.manufacturer_id.choices = manus
        self.form.item_id.default = self.itemid
        self.form.process()
        self.db.close()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern':
            command = """UPDATE substance_mixture SET manufacturer_id=%s WHERE substance_mixture_id = %s;""" % (check_value(self.form.manufacturer_id.data.split('ID:')[-1]),
                                                                                                                self.form.item_id.data)
            self.db.execute(command)
            message = u'Das Gefahrstoffgemisch wurde erfolgreich aktualisiert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
