# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField, IntegerField, TextAreaField, FloatField, BooleanField, DateField, DateTimeField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class LoginCredentials:

    login = {'login': 'restaccess', 'password': 'H9jCg768'}
    authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
    searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

    hostname = 'localhost'
    username = 'seppo'
    database = 'gefahrstoffdb'
    password = 'reldbpassword'

class SearchForm(LoginCredentials, Form):

    conn = psycopg2.connect(host=LoginCredentials.hostname, user=LoginCredentials.username, dbname=LoginCredentials.database, password=LoginCredentials.password)
    cur = conn.cursor()
    cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
    manus = cur.fetchall()
    cur.close()
    conn.close()

    #search = TextField("TextField", [validators.required()])
    manu = SelectField(u'Hersteller (SelectField):', choices=manus)

class SearchFormView(LoginCredentials, WTFormView):
    formClass = SearchForm
    buttons = ('Suche', 'Cancel')

    def submit(self, button):
        if button == 'Suche' and self.validate():

            conn = psycopg2.connect(host=LoginCredentials.hostname, user=LoginCredentials.username, password=LoginCredentials.password, dbname=LoginCredentials.database)

            cur = conn.cursor()
            cur.execute("SELECT substance_mixture_id, title FROM substance_mixture WHERE manufacturer_id = '%s';" % (self.form.manu.data))
            self.ergs = cur.fetchall()
            if self.ergs == '[]':
                self.ergs = 'Leider wurde nichts gefunden'

            cur.close()
            conn.close()
