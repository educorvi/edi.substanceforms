# -*- coding: utf-8 -*-
from wtforms import Form, StringField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()])
    description = StringField("Beschreibung", [validators.required()])
    webcode = StringField("Webcode", [validators.required()])
    address1 = StringField("Adresse 1")
    address2 = StringField("Adresse 2")
    address3 = StringField("Adresse 3")
    country = StringField("Land")
    phone = StringField("Telefon")
    fax = StringField("Telefax")
    email = StringField("E-Mail Adresse")
    homepage = StringField("Homepage")
    image_id = FileField("Bild hochladen")

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

    def submit(self, button):
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern' and self.validate():

            try:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                         '%s', '%s', '%s', '%s', %s);""" % (self.form.title.data, 
                                                            self.form.description.data,
                                                            self.context.aq_parent.get_webcode(),
                                                            check_value(self.form.address1.data),
                                                            check_value(self.form.address2.data),
                                                            check_value(self.form.address3.data),
                                                            check_value(self.form.country.data), 
                                                            check_value(self.form.phone.data),
                                                            check_value(self.form.fax.data),
                                                            check_value(self.form.email.data),
                                                            check_value(self.form.homepage.data),
                                                            check_value(self.form.image.data))
                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()
            except:
                print(u'Fehler beim Einfügen in die Datenbank')
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

