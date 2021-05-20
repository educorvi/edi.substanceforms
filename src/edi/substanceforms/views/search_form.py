# -*- coding: utf-8 -*-
from wtforms import Form, TextField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class SearchForm(Form):
    search = TextField("Suchbegriff", [validators.required()])
    two = TextField("Field Two")
    three = TextField("Field Three")

class SearchFormView(WTFormView):
    formClass = SearchForm
    buttons = ('Suche', 'Cancel')

    def submit(self, button):
        if button == 'Suche' and self.validate():
            # do fun stuff here
            login = {'login': 'restaccess', 'password': 'H9jCg768'}
            authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
            searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

            hostname = 'localhost'
            username = 'seppowalther'
            database = 'gefahrstoff'

            conn = psycopg2.connect(host=hostname, user=username, dbname=database)

            cur = conn.cursor()
            cur.execute("SELECT title FROM manufacturer WHERE title = '%s';" % (self.form.search.data))
            self.ergs = cur.fetchall()
            cur.close()
            conn.close()

            #self.ergs = 'Leider wurde nichts gefunden'
