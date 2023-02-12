# -*- coding: utf-8 -*-
import requests
from wtforms import Form, SelectField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.config import addrole
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
from edi.substanceforms.helpers import get_vocabulary, tableheads
from edi.substanceforms.content.tabelle import possibleColumns
from jinja2 import Template

class BaseForm(Form):
    """Base Form"""

class TabelleFormView(WTFormView):
    formClass = BaseForm
    buttons = ('Suche', 'Alle anzeigen')

    def __call__(self):
        self.columnids = self.getindexfortablename()
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)

        self.preselects = self.get_preselects()

        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        else:
            button = "Alle anzeigen"
            result = self.submit(button)
            if result:
                return result
        return self.index()

    def get_tablescript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/tabelle.js'

    def get_searchscript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/search.js'

    def get_hiddenscript(self):
        return ploneapi.portal.get().absolute_url() + '/++resource++edi.substanceforms/hidden.js'

    def get_preselects(self):
        moreresultcolumns = self.context.moreresultcolumns
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
        conn = self.db.connect()
        erg = list()
        res = list()
        for select in preselects:
            if not erg:
                sel = Template(select).render(value=value)
                resu = conn.execute(sel)
                resu = [i[0] for i in resu]
                if vocab:
                    erg = self.get_attr_translation(vocab, resu[0])
                else:
                    erg = resu
            else:
                res = erg
                erg = []
                for entry in res:
                    if not entry:
                        return ''
                    sel = Template(select).render(value=entry)
                    resu = conn.execute(sel)
                    if vocab:
                        result = self.get_attr_translation(vocab, resu[0])
                    else:
                        result = resu
                    erg += [i[0] for i in result]

        if vocab:
            result = erg
        else:
            result = ', '.join(erg)
        conn.close()
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

        conn = self.db.connect()
        results = conn.execute(select)
        conn.close()

        return results


    def submit(self, button):
        if button == 'Alle anzeigen':
            self.ergs = self.show_all()

        if button == 'Suche':
            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename

            select = "SELECT * FROM %s WHERE manufacturer_id = '%s';" % (searchkey, searchtable, manu_id)
            conn = self.db.connect()
            self.ergs = conn.execute(select)
            conn.close()

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)

class HerstellerForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control edi-select'})

class SubstanceForm (BaseForm):
    substance_id = SelectField(u"Suchbegriff", choices=[], render_kw={'class': 'form-control edi-select'})

class SubstanceMixtureForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control edi-select'})

class SprayPowderForm (BaseForm):
    manu = SelectField(u'Bitte wählen Sie einen Hersteller aus:', choices=[], render_kw={'class':'form-control edi-select'})

class HerstellerFormView(TabelleFormView):
    """ Erbt von TabelleFormView damit steht mit self.db eine Instanz der DB2Connect zur Verfügung """

    formClass = HerstellerForm

    def renderForm(self):
        conn = self.db.connect()
        erg = conn.execute("SELECT manufacturer_id, title FROM manufacturer ORDER BY title;")
        manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
        conn.close()
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
            conn = self.db.connect()
            self.ergs = conn.execute(select)
            conn.close()

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)


class SubstanceFormView(TabelleFormView):
    buttons = ('Suche', 'Abbrechen')
    formClass = SubstanceForm

    def renderForm(self):
        conn = self.db.connect()
        select = "SELECT substance_id, title, casnr, egnr FROM substance ORDER BY title;"
        substances = conn.execute(select)
        conn.close()
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
                conn = self.db.connect()
                self.ergs = conn.execute(select)
                conn.close()


class SubstancemixtureFormView(TabelleFormView):
    formClass = SubstanceMixtureForm

    def renderForm(self):
        select = ""
        manus = []
        mixturetype = self.context.mixturetype

        if len(mixturetype) == 1:
            select = "SELECT DISTINCT substance_mixture.manufacturer_id, manufacturer.title FROM manufacturer, substance_mixture WHERE substance_mixture.manufacturer_id = manufacturer.manufacturer_id AND substance_type = '%s' ORDER BY title;" % (mixturetype[0])
        elif len(mixturetype) > 1:
            beginselect = "SELECT DISTINCT substance_mixture.manufacturer_id, manufacturer.title FROM manufacturer, substance_mixture WHERE substance_mixture.manufacturer_id = manufacturer.manufacturer_id AND (substance_type = '%s'" % (mixturetype[0])
            select = select + beginselect
            for i in mixturetype[1:]:
                addedselect = " OR substance_type = '%s'" % i
                select = select + addedselect
            endselect = ") ORDER BY title;"
            select = select + endselect

        if mixturetype and select:
            conn = self.db.connect()
            erg = conn.execute(select)
            conn.close()
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]

        self.form.manu.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Alle anzeigen':

            mixturetype = self.context.mixturetype
            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename

            if mixturetype:
                if len(mixturetype) == 1:
                    select = "SELECT * FROM %s WHERE substance_type = '%s';" % (searchtable, mixturetype[0])
                else:
                    select = ""
                    beginselect = "SELECT * FROM %s WHERE substance_type = '%s'" % (searchtable, mixturetype[0])
                    select = select + beginselect
                    for i in mixturetype[1:]:
                        addedselect = " OR substance_type = '%s'" % i
                        select = select + addedselect
                    endselect = ";"

                    select = select + endselect

                conn = self.db.connect()
                self.ergs = conn.execute(select)
                conn.close()

            else:
                self.ergs = self.show_all()

        elif button == 'Suche':

            searchkey = self.context.tablename + '_id'
            searchtable = self.context.tablename
            manu_id = int(self.form.manu.data.split('ID:')[-1])
            mixturetype = self.context.mixturetype

            if manu_id == 'alle':
                select = "SELECT * FROM %s;" % (searchkey, searchtable)
            else:
                select = "SELECT * FROM %s WHERE manufacturer_id = %s AND substance_type = '%s';" % (searchtable, manu_id, mixturetype[0])

            conn = self.db.connect()
            self.ergs = conn.execute(select)
            conn.close()

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)


class SpraypowderFormView(TabelleFormView):
    formClass = SprayPowderForm

    def renderForm(self):
        manus = []
        select = "SELECT DISTINCT spray_powder.manufacturer_id, manufacturer.title FROM manufacturer, spray_powder WHERE spray_powder.manufacturer_id = manufacturer.manufacturer_id ORDER BY title;"
        conn = self.db.connect()
        erg = conn.execute(select)
        conn.close()
        manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
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

            select = "SELECT * FROM %s WHERE manufacturer_id = %s;" % (searchtable, manu_id)

            conn = self.db.connect()
            self.ergs = conn.execute(select)
            conn.close()

        elif button == 'Abbrechen':
            url = self.context.aq_parent.absolute_url()
            return self.request.response.redirect(url)
