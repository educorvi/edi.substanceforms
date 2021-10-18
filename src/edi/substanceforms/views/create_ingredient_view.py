# -*- coding: utf-8 -*-

import transaction
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField
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

    substance = SelectField("Reinstoff", choices=branchen, render_kw={'class': 'form-control'})
    concentration = IntegerField(u"Konzentration", render_kw={'class': 'form-control'})

class CreateIngredientForm(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        import pdb; pdb.set_trace()
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

