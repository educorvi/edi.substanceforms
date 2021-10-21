# -*- coding: utf-8 -*-

import transaction
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField, HiddenField
from plone.namedfile import NamedBlobImage
from wtforms import FileField, RadioField, SelectMultipleField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value, list_handler
from edi.substanceforms.vocabularies import substance_types, hskategorie, produktkategorien, produktklassen, branchen
from edi.substanceforms.vocabularies import classifications, usecases, application_areas
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import requests
import psycopg2

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class CreateForm(Form):

    title = StringField(u"Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField(u"Beschreibung", [validators.required()], render_kw={'class': 'form-control'})
    branch = SelectField("Branche", choices=branchen, render_kw={'class': 'form-control'})
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()], render_kw={'class': 'form-control'})
    substance_type = RadioField(u"Art des Wasch- und Reinigungsmittels", [validators.required()], choices=substance_types)
    offset_print_manner = StringField(u"Offsetdruckverfahren", render_kw={'class': 'form-control'})
    detergent_special = BooleanField(u"Es handelt sich um einen Sonderreiniger", render_kw={'class': 'form-check-input'})
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor bei 150 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor bei 160 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor bei 170 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor bei 180 Grad Celsius", render_kw={'class': 'form-control'})
    ueg = StringField(u"UEG", render_kw={'class': 'form-control'})
    response = StringField(u"Response-Faktor", render_kw={'class': 'form-control'})
    skin_category = SelectField(u"Hautschutz-Kategorie", choices=hskategorie, render_kw={'class': 'form-control'})
    date_checked = DateField(u"Datum der letzten Prüfung", render_kw={'class': 'form-control'})
    checked_emissions = BooleanField(u"Emissionsarmes Produkt", render_kw={'class': 'form-check-input'})
    flashpoint = IntegerField(u"Flammpunkt", render_kw={'class': 'form-control'})
    values_range = BooleanField(u"Wertebereich", render_kw={'class': 'form-check-input'})
    usecases = MultiCheckboxField(u"Anwendungsfälle", choices=usecases)
    application_areas = MultiCheckboxField(u"Anwendungsbereiche", choices=application_areas)
    image_url = FileField("Bilddatei hochladen", render_kw={'class': 'form-control'})
    comments = TextAreaField("Bemerkungen", render_kw={'class': 'form-control'})

class UpdateForm(Form):

    title = StringField(u"Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField(u"Beschreibung", [validators.required()], render_kw={'class': 'form-control'})
    branch = SelectField("Branche", choices=branchen, render_kw={'class': 'form-control'})
    substance_type = RadioField(u"Art des Wasch- und Reinigungsmittels", [validators.required()], choices=substance_types)
    offset_print_manner = StringField(u"Offsetdruckverfahren", render_kw={'class': 'form-control'})
    detergent_special = BooleanField(u"Es handelt sich um einen Sonderreiniger", render_kw={'class': 'form-check-input'})
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor bei 150 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor bei 160 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor bei 170 Grad Celsius", render_kw={'class': 'form-control'})
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor bei 180 Grad Celsius", render_kw={'class': 'form-control'})
    ueg = StringField(u"UEG", render_kw={'class': 'form-control'})
    response = StringField(u"Response-Faktor", render_kw={'class': 'form-control'})
    skin_category = SelectField(u"Hautschutz-Kategorie", choices=hskategorie, render_kw={'class': 'form-control'})
    date_checked = DateField(u"Datum der letzten Prüfung", render_kw={'class': 'form-control'})
    checked_emissions = BooleanField(u"Emissionsarmes Produkt", render_kw={'class': 'form-check-input'})
    flashpoint = IntegerField(u"Flammpunkt", render_kw={'class': 'form-control'})
    values_range = BooleanField(u"Wertebereich", render_kw={'class': 'form-check-input'})
    usecases = MultiCheckboxField(u"Anwendungsfälle", choices=usecases)
    application_areas = MultiCheckboxField(u"Anwendungsbereiche", choices=application_areas)
    image_url = FileField("Bilddatei hochladen", render_kw={'class': 'form-control'})
    comments = TextAreaField("Bemerkungen", render_kw={'class': 'form-control'})
    no_image = BooleanField("Vorhandenes Bild entfernen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        return self.index()

    def renderForm(self):
        try:
            insert = "SELECT manufacturer_id, title FROM manufacturer ORDER BY title;"
            manus = self.db.execute(insert)
        except:
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
        image_url = ''
        if self.form.image_url.data.filename:
            image_url = self.create_image(self.form.image_url, self.form.title.data)
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():

            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            insert = """INSERT INTO substance_mixture (title, description, webcode, branch, substance_type,
                                                        offset_print_manner, detergent_special, application_areas,
                                                        usecases, evaporation_lane_150, evaporation_lane_160,
                                                        evaporation_lane_170, evaporation_lane_180, ueg, response,
                                                        skin_category, checked_emissions, date_checked, flashpoint,
                                                        values_range, comments, image_url, manufacturer_id)
                                                        VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s',
                                                        '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                                        %s, %s);""" \
                                                        % (self.form.title.data,
                                                        self.form.description.data,
                                                        self.context.aq_parent.get_webcode(),
                                                        check_value(self.form.branch.data),
                                                        self.form.substance_type.data,
                                                        self.form.offset_print_manner.data,
                                                        self.form.detergent_special.data,
                                                        list_handler(self.form.application_areas.data),
                                                        list_handler(self.form.usecases.data),
                                                        check_value(self.form.evaporation_lane_150.data),
                                                        check_value(self.form.evaporation_lane_160.data),
                                                        check_value(self.form.evaporation_lane_170.data),
                                                        check_value(self.form.evaporation_lane_180.data),
                                                        check_value(self.form.ueg.data),
                                                        check_value(self.form.response.data),
                                                        check_value(self.form.skin_category.data),
                                                        self.form.checked_emissions.data,
                                                        check_value(self.form.date_checked.data),
                                                        check_value(self.form.flashpoint.data),
                                                        self.form.values_range.data,
                                                        check_value(self.form.comments.data),
                                                        check_value(image_url),
                                                        self.form.manufacturer_id.data)

            if self.form.image_url.data.filename:

                try:
                    self.db.execute(insert)
                    message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                    ploneapi.portal.show_message(message=message, type='info', request=self.request)
                except:
                    imageobj = ploneapi.content.get(UID=image_url)
                    ploneapi.content.delete(imageobj)

                    message = u'Fehler beim Hinzufügen des Gefahrstoffgemisches'
                    ploneapi.portal.show_message(message=message, type='error', request=self.request)

                self.db.close()

            else:
                self.db.execute(insert)
                self.db.close()
                message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)

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
        getter = """SELECT title, description, branch, substance_type, offset_print_manner, detergent_special,
                    application_areas, usecases, evaporation_lane_150, evaporation_lane_160, evaporation_lane_170,
                    evaporation_lane_180, ueg, response, skin_category, checked_emissions, date_checked, flashpoint,
                    values_range, comments, image_url
                    FROM %s WHERE %s_id = %s;""" % (self.context.tablename,
                                                    self.context.tablename,
                                                    self.itemid)
        self.result = self.db.execute(getter)
        self.db.close()
        return self.index()

    def renderForm(self):
        self.form.title.default=self.result[0][0]
        self.form.description.default=self.result[0][1]
        self.form.branch.default = self.result[0][2]
        self.form.substance_type.default = self.result[0][3]
        import pdb; pdb.set_trace()
        self.form.offset_print_manner.default = self.result[0][4]
        self.form.detergent_special.default = self.result[0][5]
        self.form.application_areas.default = self.result[0][6]
        self.form.usecases.default = self.result[0][7]
        self.form.evaporation_lane_150.default = self.result[0][8]
        self.form.evaporation_lane_160.default = self.result[0][9]
        self.form.evaporation_lane_170.default = self.result[0][10]
        self.form.evaporation_lane_180.default = self.result[0][11]
        self.form.ueg.default = self.result[0][12]
        self.form.response.default = self.result[0][13]
        self.form.skin_category.default = self.result[0][14]
        self.form.checked_emissions.default = self.result[0][15]
        self.form.date_checked.default = self.result[0][16]
        self.form.flashpoint.default = self.result[0][17]
        self.form.values_range.default = self.result[0][18]
        self.form.comments.default = self.result[0][19]
        self.form.image_url.default = self.result[0][20]
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():
            command = """UPDATE substance_mixture SET title='%s', description='%s', branch='%s', substance_type='%s',
                         offset_print_manner='%s', detergent_special=%s, application_areas='%s', usecases='%s',
                         evaporation_lane_150=%s, evaporation_lane_160=%s, evaporation_lane_170=%s, evaporation_lane_180=%s,
                         ueg='%s', response='%s', skin_category='%s', checked_emissions=%s,
                         flashpoint=%s, values_range=%s, comments='%s'
                         WHERE substance_mixture_id = %s;""" % (self.form.title.data,
                                                        self.form.description.data,
                                                        self.form.branch.data,
                                                        self.form.substance_type,
                                                        self.form.offset_print_manner.data,
                                                        self.form.detergent_special.data,
                                                        self.form.application_areas.data,
                                                        self.form.usecases.data,
                                                        check_value(self.form.evaporation_lane_150.data),
                                                        check_value(self.form.evaporation_lane_160.data),
                                                        check_value(self.form.evaporation_lane_170.data),
                                                        check_value(self.form.evaporation_lane_180.data),
                                                        self.form.ueg.data,
                                                        self.form.response.data,
                                                        self.form.skin_category.data,
                                                        self.form.checked_emissions.data,
                                                        self.form.flashpoint.data,
                                                        self.form.values_range.data,
                                                        self.form.comments.data,
                                                        self.form.item_id.data)
            self.db.execute(command)
            message = u'Das Gefahrstoffgemisch wurde erfolgreich aktualisiert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            #message = u'Fehler beim Aktualisieren des Gefahrstoffgemisches'
            #ploneapi.portal.show_message(message=message, type='error', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
