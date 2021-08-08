# -*- coding: utf-8 -*-

from wtforms import Form, StringField, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2


class UpdateForm(Form):

    fields = [('title', 'Titel'), ('description', 'Beschreibung'), ('webcode', 'Webcode'), ('address1', 'Adresse 1'), ('address2', 'Adresse 2'), ('address3', 'Adresse 3'), ('country', 'Land'), ('phone', 'Telefon'), ('fax', 'Telefax'), ('email', 'E-Mail Adresse'), ('homepage', 'Homepage'), ]

    manu = SelectField(u'Hersteller:', choices=[])
    field = SelectField(u'Hersteller:', choices=fields)
    newvalue = StringField("Neuer Wert", [validators.required()])

class UpdateFormView(WTFormView):
    formClass = UpdateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
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
                insert = ''
                cur.execute(insert)
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
            except:
                print('Fehler')
