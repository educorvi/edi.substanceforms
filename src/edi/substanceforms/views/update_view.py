# -*- coding: utf-8 -*-

from wtforms import Form, TextField, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.views.search_form import LoginCredentials
import requests
import psycopg2

myconn = LoginCredentials()

class UpdateForm(LoginCredentials, Form):

    conn = psycopg2.connect(host=LoginCredentials.hostname, user=LoginCredentials.username,
                            dbname=LoginCredentials.database, password=LoginCredentials.password)
    cur = conn.cursor()
    cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
    manus = cur.fetchall()
    cur.close()
    conn.close()

    fields = [('title', 'Titel'), ('description', 'Beschreibung'), ('webcode', 'Webcode'), ('address1', 'Adresse 1'), ('address2', 'Adresse 2'), ('address3', 'Adresse 3'), ('country', 'Land'), ('phone', 'Telefon'), ('fax', 'Telefax'), ('email', 'E-Mail Adresse'), ('homepage', 'Homepage'), ]

    manu = SelectField(u'Hersteller:', choices=manus)
    field = SelectField(u'Hersteller:', choices=fields)
    newvalue = TextField("Neuer Wert", [validators.required()])

class UpdateFormView(LoginCredentials, WTFormView):
    formClass = UpdateForm
    buttons = ('Update', 'Cancel')

    def submit(self, button):
        if button == 'Update' and self.validate():

            conn = psycopg2.connect(host=LoginCredentials.hostname, user=LoginCredentials.username, dbname=LoginCredentials.database)
            cur = conn.cursor()
            #cur.execute("INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', NULL);" % (self.form.title.data, self.form.description.data, self.form.webcode.data, self.form.address1.data, self.form.address2.data, self.form.address3.data, self.form.country.data, self.form.phone.data, self.form.fax.data, self.form.email.data, self.form.homepage.data))
            cur.execute("UPDATE manufacturer SET %s = '%s' WHERE manufacturer_id = %s;" % (self.form.field.data, self.form.newvalue.data, self.form.manu.data))
            #cur.execute("UPDATE manufacturer SET address2 = NULL WHERE address2 = '';")
            #cur.execute("UPDATE manufacturer SET address3 = NULL WHERE address3 = '';")
            #cur.execute("UPDATE manufacturer SET country = NULL WHERE country = '';")
            #cur.execute("UPDATE manufacturer SET phone = NULL WHERE phone = '';")
            #cur.execute("UPDATE manufacturer SET fax = NULL WHERE fax = '';")
            #cur.execute("UPDATE manufacturer SET email = NULL WHERE email = '';")
            #cur.execute("UPDATE manufacturer SET homepage = NULL WHERE homepage = '';")
            #import pdb; pdb.set_trace()
            conn.commit()
            cur.close()
            conn.close()
