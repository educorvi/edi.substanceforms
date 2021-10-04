# -*- coding: utf-8 -*-
from wtforms import Form, TextField, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
from plone import api as ploneapi
from edi.substanceforms.config import addrole
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

class GeneralizedForm(Form):

    search = TextField("Suchbegriff")
    #manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[])

class TabelleFormView(WTFormView):
    formClass = GeneralizedForm
    buttons = ('Suche', 'Abbrechen')

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

    def userCanAdd(self):
        if not ploneapi.user.is_anonymous():
            current = ploneapi.user.get_current()
            roles = ploneapi.user.get_roles(user=current)
            if addrole in roles or 'Manager' in roles or 'Site Administrator' in roles:
                return self.context.absolute_url() + '/create-%s-form' % self.context.tablename
        return False

    def renderForm(self):
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
            manus = cur.fetchall()
            cur.close
            conn.close()
        except:
            manus = []
        #self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()


    def submit(self, button):
        #if button == 'Suche' and self.validate():
        if button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            #manu_id = self.form.manu.data

            select = "SELECT %s, title FROM %s WHERE manufacturer_id = '%s';" % (searchkey, searchtable, manu_id)
            try:
                conn = psycopg2.connect(host=self.host, user=self.username, password=self.password, dbname=self.dbname)
                cur = conn.cursor()
                cur.execute(select)
                self.ergs = cur.fetchall()
                cur.close
                conn.close()

            except:
                self.ergs = []

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)

class HerstellerForm (TabelleFormView):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[])
