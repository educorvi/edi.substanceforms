# -*- coding: utf-8 -*-

from wtforms import Form, StringField, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.lib import DBConnect

#TODO: what the hell does this do?

class UpdateForm(Form):

    fields = [('title', 'Titel'), ('description', 'Beschreibung'), ('webcode', 'Webcode'), ('address1', 'Adresse 1'), ('address2', 'Adresse 2'), ('address3', 'Adresse 3'), ('country', 'Land'), ('phone', 'Telefon'), ('fax', 'Telefax'), ('email', 'E-Mail Adresse'), ('homepage', 'Homepage'), ]

    manu = SelectField(u'Hersteller:', choices=[])
    field = SelectField(u'Hersteller:', choices=fields)
    newvalue = StringField("Neuer Wert", [validators.required()])

class UpdateFormView(WTFormView):
    formClass = UpdateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        return self.index()

    def submit(self, button):
        if button == 'Speichern' and self.validate():
            conn = self.db.connect()
            insert = ''
            conn.execute(insert)
            conn.close()
