# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class CreateForm(Form):

    title = TextField("Titel", [validators.required()])
    description = TextField("Beschreibung", [validators.required()])
    webcode = TextField("Webcode", [validators.required()])
    address1 = TextField("Adresse 1")
    address2 = TextField("Adresse 2")
    address3 = TextField("Adresse 3")
    country = TextField("Land")
    phone = TextField("Telefon")
    fax = TextField("Telefax")
    email = TextField("E-Mail Adresse")
    homepage = TextField("Homepage")

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        self.ergs = []
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        return self.index()

    def submit(self, button):
        if button == 'Speichern' and self.validate():

            try:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                         '%s', '%s', '%s', '%s', NULL);""" % (self.form.title.data, 
                                                              self.form.description.data,
                                                              self.form.webcode.data,
                                                              self.form.address1.data,
                                                              self.form.address2.data,
                                                              self.form.address3.data,
                                                              self.form.country.data, 
                                                              self.form.phone.data,
                                                              self.form.fax.data,
                                                              self.form.email.data,
                                                              self.form.homepage.data)
                cur.execute(insert)
                cur.execute("UPDATE manufacturer SET address1 = NULL WHERE address1 = '';")
                cur.execute("UPDATE manufacturer SET address2 = NULL WHERE address2 = '';")
                cur.execute("UPDATE manufacturer SET address3 = NULL WHERE address3 = '';")
                cur.execute("UPDATE manufacturer SET country = NULL WHERE country = '';")
                cur.execute("UPDATE manufacturer SET phone = NULL WHERE phone = '';")
                cur.execute("UPDATE manufacturer SET fax = NULL WHERE fax = '';")
                cur.execute("UPDATE manufacturer SET email = NULL WHERE email = '';")
                cur.execute("UPDATE manufacturer SET homepage = NULL WHERE homepage = '';")
                #import pdb; pdb.set_trace()
                conn.commit()
                cur.close()
                conn.close()
            except:
                print(u'Fehler beim Einfügen in die Datenbank')
