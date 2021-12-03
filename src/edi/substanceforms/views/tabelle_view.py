# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField, IntegerField, BooleanField, FloatField
from wtforms import validators
from collective.wtforms.views import WTFormView
from plone import api as ploneapi
from edi.substanceforms.config import addrole
import requests
import psycopg2
from plone import api as ploneapi

class LoginCredentials:

    login = {'login': 'restaccess', 'password': 'H9jCg768'}
    authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
    searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

    hostname = 'localhost'
    username = 'seppo'
    database = 'gefahrstoffdb'
    password = 'reldbpassword'

class BaseForm(Form):

    search = StringField("Suchbegriff", render_kw={'class':'form-control'})
    #manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[])

class TabelleFormView(WTFormView):
    formClass = BaseForm
    buttons = ('Suche', 'Alle anzeigen', 'Abbrechen')

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

    def show_all(self):
        results = []
        searchkey = self.context.tablename + '_id'
        searchtable = self.context.tablename
        select = "SELECT %s, title FROM %s ORDER BY title ASC;" % (searchkey, searchtable)
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, password=self.password, dbname=self.dbname)
            cur = conn.cursor()
            cur.execute(select)
            results = cur.fetchall()
            cur.close
            conn.close()

        except:
            results = []
        #results = select um alle Produkte der Tabelle auszuwählen
        return results


    def submit(self, button):
        #if button == 'Suche' and self.validate():
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
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

class HerstellerForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control'})

class SubstanceForm (BaseForm):
    casnr = IntegerField(u'Bitte geben Sie eine CAS-Nummer an:', render_kw={'class':'form-control'})
    concentration = IntegerField(u'Bitte geben Sie eine Konzentration in wässriger Lösung an:', render_kw={'class':'form-control'})

class SubstanceMixtureForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control'})
    detergent_special = BooleanField(u'Nur Sonderreiniger anzeigen?', render_kw={'class':'form-check-input'})

class SprayPowderForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control'})
    median_value = FloatField(u'Bitte geben Sie den Medianwert ein', render_kw={'class':'form-control'})
    volume_share = FloatField(u'Bitte geben Sie den Volumenanteil ein', render_kw={'class':'form-control'})

class HerstellerFormView(TabelleFormView):
    formClass = HerstellerForm

    def renderForm(self):
        manus = [('alle', 'Alle anzeigen')]
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            manus += cur.fetchall()
            cur.close
            conn.close()
        except:
            manus += []
        self.form.manu.choices = manus
        #self.form.manu.default = 'alle'
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = self.form.manu.data

            if manu_id == 'alle':
                select = "SELECT %s, title FROM %s;" % (searchkey, searchtable)
            else:
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

class SubstanceFormView(TabelleFormView):
    formClass = SubstanceForm

    def renderForm(self):
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            casnr = self.form.casnr.data
            concentration = self.form.concentration.data

            if casnr and concentration:
                select = "SELECT %s, title FROM %s WHERE casnr = '%s' AND concentration = '%s';" % (searchkey, searchtable, casnr, concentration)
            elif casnr:
                select = "SELECT %s, title FROM %s WHERE casnr = '%s';" % (searchkey, searchtable, casnr)
            elif concentration:
                select = "SELECT %s, title FROM %s WHERE concentration = '%s';" % (searchkey, searchtable, concentration)

            try:
                conn = psycopg2.connect(host=self.host, user=self.username, password=self.password, dbname=self.dbname)
                cur = conn.cursor()
                cur.execute(select)
                self.ergs = cur.fetchall()
                cur.close
                conn.close()

            except:
                self.ergs = []

class SubstancemixtureFormView(TabelleFormView):
    formClass = SubstanceMixtureForm

    def renderForm(self):
        manus = [('alle', 'Alle anzeigen')]
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            manus += cur.fetchall()
            cur.close
            conn.close()
        except:
            manus += []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = self.form.manu.data
            is_detergent_special = self.form.detergent_special.data

            if manu_id == 'alle' and is_detergent_special == True:
                select = "SELECT %s, title FROM %s WHERE detergent_special = True;" % (searchkey, searchtable)
            elif manu_id == 'alle':
                select = "SELECT %s, title FROM %s;" % (searchkey, searchtable)
            elif is_detergent_special == True:
                select = "SELECT %s, title FROM %s WHERE manufacturer_id = %s AND detergent_special = True;" % (searchkey, searchtable, manu_id)
            else:
                select = "SELECT %s, title FROM %s WHERE manufacturer_id = %s;" % (searchkey, searchtable, manu_id)

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

class SpraypowderFormView(TabelleFormView):
    formClass = SprayPowderForm

    def renderForm(self):
        manus = [('alle', 'Alle anzeigen')]
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            manus += cur.fetchall()
            cur.close
            conn.close()
        except:
            manus += []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
        """
        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = self.form.manu.data
            is_detergent_special = self.form.detergent_special.data

            if manu_id == 'alle' and is_detergent_special == True:
                select = "SELECT %s, title FROM %s WHERE detergent_special = True;" % (searchkey, searchtable)
            elif manu_id == 'alle':
                select = "SELECT %s, title FROM %s;" % (searchkey, searchtable)
            elif is_detergent_special == True:
                select = "SELECT %s, title FROM %s WHERE manufacturer_id = '%s' AND detergent_special = True;" % (searchkey, searchtable, manu_id)
            else:
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
        """
