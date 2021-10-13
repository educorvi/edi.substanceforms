# -*- coding: utf-8 -*-
import transaction
from wtforms import Form, StringField, SelectField, IntegerField, FileField, FloatField, BooleanField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import hskategorie, branchen, product_class
from plone.namedfile import NamedBlobImage
from edi.substanceforms.views.create_mixture_form import MultiCheckboxField
from plone import api as ploneapi
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", [validators.required()], render_kw={'class': 'form-control'})
    manufacturer_id = SelectField(u"Hersteller des Druckbestäubungspuders", [validators.required()], render_kw={'class': 'form-control'})
    product_class = SelectField("Produktklasse", choices=product_class, render_kw={'class': 'form-control'})
    starting_material = StringField("Ausgangsmaterial", render_kw={'class': 'form-control'})
    median_value = FloatField("Medianwert", render_kw={'class': 'form-control'})
    volume_share = FloatField("Volumenanteil", render_kw={'class': 'form-control'})
    checked_emissions = BooleanField("Emissionsgeprüft", render_kw={'class': 'form-check-input'})
    date_checked = StringField("Prüfdatum", render_kw={'class': 'form-control'})
    image_url = FileField("Bild hochladen", render_kw={'class': 'form-control'})

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
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
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            manus = cur.fetchall()
            cur.close
            conn.close()
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
            insert = """INSERT INTO spray_powder VALUES (DEFAULT, '%s', '%s', '%s',
                        %s, %s, %s, %s, %s, %s, %s, %s);""" % (self.form.title.data,
                                                       self.form.description.data,
                                                       self.context.aq_parent.get_webcode(),
                                                       check_value(self.form.product_class.data),
                                                       check_value(self.form.starting_material.data),
                                                       check_value(self.form.median_value.data),
                                                       check_value(self.form.volume_share.data),
                                                       check_value(self.form.checked_emissions.data),
                                                       check_value(self.form.date_checked.data),
                                                       check_value(image_url),
                                                       self.form.manufacturer_id.data)

            if self.form.image_url.data.filename:

                try:
                    cur.execute(insert)
                    conn.commit()

                    message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                    ploneapi.portal.show_message(message=message, type='info', request=self.request)
                except:
                    imageobj = ploneapi.content.get(UID=image_url)
                    ploneapi.content.delete(imageobj)

                    message = u'Fehler beim Hinzufügen des Gefahrstoffgemisches'
                    ploneapi.portal.show_message(message=message, type='error', request=self.request)

                cur.close()
                conn.close()

            else:
                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()

                message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)

            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

