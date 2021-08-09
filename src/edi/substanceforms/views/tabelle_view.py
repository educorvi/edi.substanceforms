# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField
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

class SearchForm(Form):

    search = TextField("Suchbegriff")
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[])

class TabelleFormView(WTFormView):
    formClass = SearchForm
    buttons = ('Suche', 'Cancel')

    def __call__(self):
        self.ergs = []
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        return self.index()

    def userCanAdd(self):
        if not ploneapi.user.is_anonymous():
            current = ploneapi.user.get_current()
            roles = ploneapi.user.get_roles(user=current)
            if addrole in roles:
                return self.context.absolute_url() + '/create-%s-form' % self.context.tablename
        return False

    def renderForm(self):
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
            #TODO: Manufacturer must have a valid reference in self.context.tablename 
            manus = cur.fetchall()
            cur.close
            conn.close()
        except:
            manus = []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()


    def submit(self, button):
        if button == 'Suche' and self.validate():
            manu_id = self.form.manu.data
            select = "SELECT substance_mixture_id, title FROM substance_mixture WHERE manufacturer_id = '%s';" %manu_id
            try:
                conn = psycopg2.connect(host=self.host, user=self.username, password=self.password, dbname=self.dbname)
                cur = conn.cursor()
                cur.execute(select)
                self.ergs = cur.fetchall() #TODO: In welchem Format lesen wir die Ergebnisse? String? Liste?
                cur.close
                conn.close()
            except:
                self.ergs = []
