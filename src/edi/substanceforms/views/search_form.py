# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField, IntegerField, TextAreaField, FloatField, BooleanField, DateField, DateTimeField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class logincredentials:
    login = {'login': 'restaccess', 'password': 'H9jCg768'}
    authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
    searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

    hostname = 'localhost'
    username = 'postgres'
    database = 'gefahrstoff'

class SearchForm(logincredentials, Form):

    conn = psycopg2.connect(host=logincredentials.hostname, user=logincredentials.username, dbname=logincredentials.database)
    cur = conn.cursor()
    cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
    manus = cur.fetchall()
    cur.close()
    conn.close()

    search = TextField("TextField", [validators.required()])
    text = TextAreaField("TextAreaField")
    manu = SelectField(u'Hersteller (SelectField):', choices=manus)
    zahl = IntegerField("IntegerField")
    float = FloatField("FloatField")
    boool = BooleanField("BooeleanField")
    date = DateField("DateField")
    datetime = DateTimeField("DateTimeField")

class SearchFormView(logincredentials, WTFormView):
    formClass = SearchForm
    buttons = ('Suche', 'Cancel')

    def submit(self, button):
        if button == 'Suche' and self.validate():

            conn = psycopg2.connect(host=logincredentials.hostname, user=logincredentials.username, dbname=logincredentials.database)

            cur = conn.cursor()
            cur.execute("SELECT title FROM manufacturer WHERE manufacturer_id = '%s';" % (self.form.manu.data))
            self.ergs = cur.fetchall()
            if self.ergs == '[]':
                self.ergs = 'Leider wurde nichts gefunden'

            cur.close()
            conn.close()
