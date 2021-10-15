# -*- coding: utf-8 -*-
import transaction
from wtforms import Form, StringField, SelectField, IntegerField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import hskategorie, branchen
from plone.namedfile import NamedBlobImage
from edi.substanceforms.views.create_mixture_form import MultiCheckboxField
from plone import api as ploneapi
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", [validators.required()], render_kw={'class': 'form-control'})
    casnr = IntegerField("CAS-Nummer", [validators.required()], render_kw={'class': 'form-control'})
    concentration = IntegerField("Konzentration in wässriger Lösung", render_kw={'class': 'form-control'})
    skin_category = SelectField("Hautschutzkategorie", choices = hskategorie, render_kw={'class': 'form-control'})
    branch = SelectField("Branche", choices = branchen, render_kw={'class': 'form-control'})
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
            insert = """INSERT INTO substance VALUES (DEFAULT, '%s', '%s', '%s',
                        %s, %s, %s, %s, %s);""" % (self.form.title.data,
                                                       self.form.description.data,
                                                       self.context.aq_parent.get_webcode(),
                                                       check_value(self.form.casnr.data),
                                                       check_value(self.form.concentration.data),
                                                       check_value(self.form.skin_category.data),
                                                       check_value(self.form.branch.data),
                                                       check_value(image_url))

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

class UpdateFormView(CreateFormView):

    def __call__(self):
        import pdb;pdb.set_trace()
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        self.itemid = self.request.get('itemid')
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        getter = "SELECT image_url FROM %s WHERE %s_id = %s;" % (self.context.tablename,
                                                                 self.context.tablename,
                                                                 self.itemid)
        cur.execute(getter)
        self.result = cur.fetchall()
        cur.close()
        conn.close()
        return self.index()
"""
    def renderForm(self):
        image_uid = self.result[0][0]
        image_obj = ploneapi.content.get(UID=image_uid)
        self.form.image_url.data = image_obj.image.data
        self.form.process()
"""
