# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField, IntegerField, BooleanField, FloatField
from wtforms import validators
from collective.wtforms.views import WTFormView
from plone import api as ploneapi
from edi.substanceforms.config import addrole
import requests
import psycopg2
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
from edi.substanceforms.helpers import get_vocabulary, tableheads
from edi.substanceforms.content.tabelle import possibleColumns
from jinja2 import Template



class LoginCredentials:

    login = {'login': 'restaccess', 'password': 'H9jCg768'}
    authurl = u'http://emissionsarme-produkte.bgetem.de/@login'
    searchurl = u'http://emissionsarme-produkte.bgetem.de/@search'

    hostname = 'localhost'
    username = 'seppo'
    database = 'gefahrstoffdb'
    password = 'reldbpassword'

class BaseForm(Form):
    """Base Form"""

    #search = StringField("Suchbegriff", render_kw={'class':'form-control'})
    #manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[])

class TabelleFormView(WTFormView):
    formClass = BaseForm
    buttons = ('Suche', 'Alle anzeigen', 'Abbrechen')

    def __call__(self):
        self.columnids = self.getindexfortablename()
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)

        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        self.preselects = self.get_preselects()
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        return self.index()

    def get_preselects(self):
        moreresultcolumns = self.context.moreresultcolumns
        #brains = self.context.getFolderContents()
        preselects = []
        for i in moreresultcolumns:
            entry = dict()
            obj = self.context[i]
            entry['id'] = obj.id
            entry['title'] = obj.title
            entry['preselects'] = obj.preselects
            entry['vocab'] = obj.vocab
            preselects.append(entry)
        return preselects

    def get_preergs(self, preselects, vocab, value):
        erg = list()
        for select in preselects:
            if not erg:
                sel = Template(select).render(value=value)
                try:
                    resu = self.db.execute(sel)
                    resu = [i[0] for i in resu]
                    if vocab:
                        import pdb; pdb.set_trace()
                        erg = self.get_attr_translation(vocab, resu[0])
                    else:
                        erg = resu
                except:
                    erg = ' '
            else:
                res = erg
                erg = []
                for entry in res:
                    sel = Template(select).render(value=entry)
                    try:
                        resu = self.db.execute(sel)
                        if vocab:
                            import pdb;
                            pdb.set_trace()
                            result = self.get_attr_translation(vocab, resu[0])
                        else:
                            result = resu
                        erg += [i[0] for i in result]
                    except:
                        result = ' '

        result = ', '.join(erg)
        return result

    def getindexfortablename(self):
        columnids = list()
        for i in self.context.resultcolumns:
            columnids.append(possibleColumns(self.context).getTerm(i).token)
        return columnids

    def get_tablehead(self, column):
        result = tableheads(column)
        return result

    def userCanAdd(self):
        if not ploneapi.user.is_anonymous():
            current = ploneapi.user.get_current()
            roles = ploneapi.user.get_roles(user=current)
            if addrole in roles or 'Manager' in roles or 'Site Administrator' in roles:
                return self.context.absolute_url() + '/create-%s-form' % self.context.tablename
        return False

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value

    def show_all(self):
        results = []
        searchkey = self.context.tablename + '_id'
        searchtable = self.context.tablename
        resultcolumns = self.context.resultcolumns

        if not resultcolumns:
            select = "SELECT %s, title FROM %s WHERE status = 'published' ORDER BY title ASC;" % (searchkey, searchtable)
        else:
            select = "SELECT * FROM %s WHERE status = 'published' ORDER BY title ASC;" % (searchtable)


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

            #print(self.context.mixturetype)
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
    substance_id = SelectField(u"Suchbegriff", choices=[], render_kw={'class': 'form-control'})

class SubstanceMixtureForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control'})
class SprayPowderForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control'})
    median_value = FloatField(u'Bitte geben Sie den Medianwert ein', render_kw={'class':'form-control'})
    volume_share = FloatField(u'Bitte geben Sie den Volumenanteil ein', render_kw={'class':'form-control'})

class HerstellerFormView(TabelleFormView):
    formClass = HerstellerForm

    def renderForm(self):
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            erg = cur.fetchall()
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
            cur.close
            conn.close()
        except:
            manus = []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()
        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = self.form.manu.data.split('ID:')[-1]

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
    buttons = ('Suche', 'Abbrechen')
    formClass = SubstanceForm

    def renderForm(self):
        try:
            select = "SELECT substance_id, title, casnr, egnr FROM substance ORDER BY title;"
            substances = self.db.execute(select)
        except:
            substances = []
        optionlist = list()
        for i in substances:
            subid = i[0]
            subname = i[1]
            subcas = i[2]
            subeg = i[3]
            subentry = f"{subname} CAS:{subcas} EG:{subeg} ID:{subid}"
            optionlist.append((i[0], subentry))
        self.form.substance_id.choices = optionlist
        self.form.process()
        return self.formTemplate()


    def submit(self, button):
        if button == 'Suche':

            substance_id = self.form.substance_id.data.split('ID:')[-1]

            if substance_id:
                select = "SELECT substance_id, title FROM substance WHERE substance_id = %s;" % (substance_id)

                self.ergs = self.db.execute(select)


class SubstancemixtureFormView(TabelleFormView):
    formClass = SubstanceMixtureForm

    def renderForm(self):
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            erg = cur.fetchall()
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
            cur.close
            conn.close()
        except:
            manus = []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':

            mixturetype = self.context.mixturetype
            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename

            if mixturetype:
                select = "SELECT * FROM %s WHERE substance_type = '%s';" % (searchtable, mixturetype)
                conn = psycopg2.connect(host=self.host, user=self.username, password=self.password,
                                        dbname=self.dbname)
                cur = conn.cursor()
                cur.execute(select)
                self.ergs = cur.fetchall()
                cur.close
                conn.close()

            else:
                self.ergs = self.show_all()

        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = int(self.form.manu.data.split('ID:')[-1])

            if manu_id == 'alle':
                select = "SELECT %s, title FROM %s;" % (searchkey, searchtable)
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
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
            erg = cur.fetchall()
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
            cur.close
            conn.close()
        except:
            manus = []
        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()

        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = self.form.manu.data.split('ID:')[-1]

            select = "SELECT %s, title FROM %s WHERE manufacturer_id = %s;" % (searchkey, searchtable, manu_id)

            self.ergs = self.db.execute(select)

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)
