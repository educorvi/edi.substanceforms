# -*- coding: utf-8 -*-
from edi.substanceforms import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
from edi.substanceforms.content.tabelle import possibleColumns
from edi.substanceforms.config import editrole
from edi.substanceforms.helpers import get_vocabulary
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import psycopg2
from jinja2 import Template


from edi.substanceforms.content.tabelle import possibleColumns

class SingleView(BrowserView):

    index = ViewPageTemplateFile('standard.pt')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        self.itemid = self.request.get('item')
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        self.article = self.get_article()
        self.machines = []
        self.secsheet = []

        #import pdb; pdb.set_trace()
        self.definitions = self.get_definitions()
        print(self.definitions)

        self.more_definitions = self.get_more_definitions()

        if self.context.tablename == 'substance_mixture':
            #self.machines = self.get_machines()
            #self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('single_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        if self.context.tablename == 'substance':
            #self.machines = self.get_machines()
            #self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('single_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'spray_powder':
            template = ViewPageTemplateFile('single_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'manufacturer':
            template = ViewPageTemplateFile('single_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        return self.index()

    def get_definitions(self):
        fragments = list()
        columns = self.context.columns
        for key in columns:
            key_value_pair = getattr(self, key, None) # hole die Methode für Aufbereitung der Daten in DB-Spalte key

            if key_value_pair:
                entry = key_value_pair()
                if entry:
                    title = entry['title']
                    value = entry['value']
                    fragment = f'<dt class="col col-sm-5">{title}</dt><dd class="col col-sm-7">{value}</dd><div class="w-100 divider"></div>'
                    fragments.append(fragment)

        return fragments

    def get_more_definitions(self):
        fragments = list()
        preselects = list()
        for column in self.context.morecolumns:
            entry = dict()
            obj = self.context[column]
            entry['id'] = obj.id
            entry['title'] = obj.title
            entry['preselects'] = obj.preselects
            entry['vocab'] = obj.vocab
            preselects.append(entry)

        for select in preselects:
            title = select['title']
            value = self.get_preergs(select)
            if value:
                fragment = f'<dt class="col col-sm-5">{title}</dt><dd class="col col-sm-7">{value}</dd><div class="w-100 divider"></div>'
                fragments.append(fragment)
        return fragments

    def get_preergs(self, preselect):
        erg = list()
        vocabulary = preselect.get('vocab')
        preselects = preselect.get('preselects')
        for select in preselects:
            if not erg:
                sel = Template(select).render(value=self.itemid)
                try:
                    resu = self.db.execute(sel)
                    resu = [i[0] for i in resu]
                    if vocabulary:
                        erg = [self.get_attr_translation(vocabulary, i) for i in resu]
                    else:
                        erg = resu
                except:
                    erg = []
            else:
                res = erg
                erg = []
                for entry in res:
                    sel = Template(select).render(value=entry)
                    try:
                        resu = self.db.execute(sel)
                        if vocabulary:
                            result = [self.get_attr_translation(vocabulary, i) for i in resu]
                        else:
                            result = resu
                        erg += [i[0] for i in result]
                    except:
                        result = []
        if len(erg) == 1:
            return erg[0]
        else:
            htmlstring = '<span><ul>'
            for element in erg:
                htmlstring += f'<li>{element}</li>'
            htmlstring += '</ul></span>'
            return htmlstring

    def is_mixture(self):
        if self.context.tablename == 'substance_mixture':
            return True
        else:
            return False

    def is_substance(self):
        if self.context.tablename == 'substance':
            return True
        else:
            return False

    def is_manufacturer(self):
        if self.context.tablename == 'manufacturer':
            return True
        else:
            return False

    def is_powder(self):
        if self.context.tablename == 'spray_powder':
            return True
        else:
            return False

    def substance_type(self):
        title = "Typ des Wasch- und Reinigungsmittels"
        fieldindex = possibleColumns(self.context).getTerm('substance_type').token
        value = self.get_attr_translation('substance_type', self.article[int(fieldindex)])
        if value:
            return {'title': title, 'value': value}
        return {}

    def branch(self):
        title = "Branche"
        if self.context.tablename == 'substance_mixture':
            fieldindex = possibleColumns(self.context).getTerm('branch').token
            value = self.get_attr_translation('branch', self.article[int(fieldindex)])
        elif self.context.tablename == 'substance':
            fieldindex = possibleColumns(self.context).getTerm('branch').token
            value = self.get_attr_translation('branch', self.article[int(fieldindex)])
        if value:
            return {'title': title, 'value': value}
        return {}

    def manufacturer_id(self):
        title = "Hersteller"
        if self.context.tablename == 'substance_mixture':
            fieldindex = possibleColumns(self.context).getTerm('manufacturer_id').token
            value = self.get_manufacturer(self.article[int(fieldindex)])
        elif self.context.tablename == 'spray_powder':
            fieldindex = possibleColumns(self.context).getTerm('manufacturer_id').token
            value = self.get_manufacturer(self.article[int(fieldindex)])
        elif self.context.tablename == 'manufacturer':
            value = False
        if value:
            return {'title': title, 'value': value}
        return {}

    def skin_category(self):
        title = "Hautschutzmittelgruppe"
        if self.context.tablename == 'substance_mixture':
            fieldindex = possibleColumns(self.context).getTerm('skin_category').token
            value = self.get_attr_translation('hskategorie', self.article[int(fieldindex)])
        elif self.context.tablename == 'substance':
            fieldindex = possibleColumns(self.context).getTerm('skin_category').token
            value = self.get_attr_translation('hskategorie', self.article[int(fieldindex)])
        if value:
            return {'title': title, 'value': value}
        return {}

    def checked_emissions(self):
        title = "Emissionsarmes Produkt"
        if self.context.tablename == 'substance_mixture':
            fieldindex = possibleColumns(self.context).getTerm('checked_emissions').token
            value = self.get_attr_translation('boolvocab', str(self.article[int(fieldindex)]))
        elif self.context.tablename == 'spray_powder':
            fieldindex = possibleColumns(self.context).getTerm('checked_emissions').token
            value = self.get_attr_translation('boolvocab', str(self.article[int(fieldindex)]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_150(self):
        title = "Verdampfungsfaktor 150 Grad"
        fieldindex = possibleColumns(self.context).getTerm('evaporation_lane_150').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_160(self):
        title = "Verdampfungsfaktor 160 Grad"
        fieldindex = possibleColumns(self.context).getTerm('evaporation_lane_160').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_170(self):
        title = "Verdampfungsfaktor 170 Grad"
        fieldindex = possibleColumns(self.context).getTerm('evaporation_lane_170').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_180(self):
        title = "Verdampfungsfaktor 180 Grad"
        fieldindex = possibleColumns(self.context).getTerm('evaporation_lane_180').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def date_checked(self):
        title = "Prüfdatum"
        fieldindex = possibleColumns(self.context).getTerm('date_checked').token
        if self.context.tablename == 'substance_mixture':
            value = self.article[int(fieldindex)]
        elif self.context.tablename == 'spray_powder':
            value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def flashpoint(self):
        title = "Flammpunkt in °C"
        fieldindex = possibleColumns(self.context).getTerm('flashpoint').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def ueg(self):
        title = "UEG in g/m3"
        fieldindex = possibleColumns(self.context).getTerm('ueg').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def response(self):
        title = "Responsefaktor"
        fieldindex = possibleColumns(self.context).getTerm('response').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def application_areas(self):
        title = "Anwendungsgebiete"
        fieldindex = possibleColumns(self.context).getTerm('application_areas').token
        mixtureid = possibleColumns(self.context).getTerm('substance_mixture_id').token
        value = self.translate_application_areas(self.new_application_areas_translation2(self.article[int(mixtureid)]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def usecases(self):
        title = "Verwendungszwecke"
        fieldindex = possibleColumns(self.context).getTerm('usecases').token
        mixtureid = possibleColumns(self.context).getTerm('substance_mixture_id').token
        value = self.translate_usecases(self.new_usecase_translation2(self.article[int(mixtureid)]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def concentration(self):
        title = "Konzentration in wässriger Lösung"
        fieldindex = possibleColumns(self.context).getTerm('concentration').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def casnr(self):
        title = "CAS-Nummer"
        fieldindex = possibleColumns(self.context).getTerm('casnr').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def egnr(self):
        title = "EG-Nummer"
        fieldindex = possibleColumns(self.context).getTerm('egnr').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def dnel_lokal(self):
        title = "DNEL Inhalation [mg/m3]: lokal"
        fieldindex = possibleColumns(self.context).getTerm('dnel_lokal').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def dnel_systemisch(self):
        title = "DNEL Inhalation [mg/m3]: systemisch"
        fieldindex = possibleColumns(self.context).getTerm('dnel_systemisch').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def formula(self):
        title = "Formel"
        fieldindex = possibleColumns(self.context).getTerm('formula').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}


    def mol(self):
        title = "Molmasse [g/mol]"
        fieldindex = possibleColumns(self.context).getTerm('mol').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def homepage(self):
        title = "Homepage"
        fieldindex = possibleColumns(self.context).getTerm('homepage').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def product_class(self):
        title = "Produktklasse"
        fieldindex = possibleColumns(self.context).getTerm('product_class').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def starting_material(self):
        title = "Ausgangsmaterial"
        fieldindex = possibleColumns(self.context).getTerm('starting_material').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def volume_share(self):
        title = "Volumenanteil"
        fieldindex = possibleColumns(self.context).getTerm('volume_share').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def median_value(self):
        title = "Medianwert"
        fieldindex = possibleColumns(self.context).getTerm('median_value').token
        value = self.article[int(fieldindex)]
        if value:
            return {'title': title, 'value': value}
        return {}

    def edit_url(self):
        if self.context.tablename == 'substance_mixture':
            link = self.context.absolute_url() + '/update-mixture-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'substance':
            link = self.context.absolute_url() + '/update-substance-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'manufacturer':
            link = self.context.absolute_url() + '/update-manufacturer-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'spray_powder':
            link = self.context.absolute_url() + '/update-powder-form?itemid=%s' % self.itemid
            return link

    def delete_url(self):
        if self.context.tablename == 'substance_mixture':
            link = self.context.absolute_url()+'/delete-mixture-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'substance':
            link = self.context.absolute_url()+'/delete-substance-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'manufacturer':
            link = self.context.absolute_url() + '/delete-manufacturer-form?itemid=%s' % self.itemid
            return link
        elif self.context.tablename == 'spray_powder':
            link = self.context.absolute_url() + '/delete-powder-form?itemid=%s' % self.itemid
            return link

    def userCanEdit(self):
        if not ploneapi.user.is_anonymous():
            current = ploneapi.user.get_current()
            roles = ploneapi.user.get_roles(user=current)
            if editrole in roles or 'Manager' in roles or 'Site Administrator' in roles:
                return self.context.absolute_url() + '/update-%s-form' % self.context.tablename
        return False

    def get_article(self):
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        tablename = self.context.tablename
        select = "SELECT * from %s WHERE %s_id = %s" %(tablename, tablename, self.itemid)
        cur.execute(select)
        article = cur.fetchall()[0]
        print(article)
        cur.close
        conn.close()
        return article

    def get_image_url(self):
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        tablename = self.context.tablename
        select = "SELECT image_url from %s WHERE %s_id = %s" % (tablename, tablename, self.itemid)
        cur.execute(select)
        uid = cur.fetchall()[0][0]
        cur.close
        conn.close()

        if uid:
            imageobj = ploneapi.content.get(UID=uid)
            image_url = '%s/@@images/image/preview' % imageobj.absolute_url()
            return image_url
        else:
            return False

    """
    def get_machines(self):
        machine_titles = []
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        select = "SELECT machine_id from mixture_pairs WHERE mixture_id = %s" %self.itemid
        cur.execute(select)
        machine_ids = cur.fetchall() #TODO: muss evenutell noch behandelt werden
        cur.close()
        for i in machine_ids:
            cur = conn.cursor()
            select = "SELECT title from printing_machine WHERE printing_machine_id = %s" %i
            cur.execute(select)
            machine_title = cur.fetchall()
            cur.close()
            machine_titles.append(machine_title)
        conn.close()
        return machine_titles
    """

    def get_synonyms(self):
        synonyms = []
        select = "SELECT synonym_name from synonyms WHERE substance_id = %s" %self.itemid
        synonyms = self.db.execute(select)
        return synonyms

    def get_manufacturer(self, manu):
        select = "SELECT title from manufacturer WHERE manufacturer_id = %s" %manu
        manufacturer = self.db.execute(select)
        result = manufacturer[0][0]
        return result

    def translate_synonyms(self, synonyms):
        resultstring = ""
        index = 0
        for i in synonyms:
            resultstring = resultstring + "%s, " % (synonyms[index][0])
            index = index + 1
        resultstring = resultstring[:-2]
        return resultstring

    def get_recipes(self):
        substances = []
        select = "SELECT substance_id, concentration_min, concentration_max from recipes WHERE mixture_id = %s" %self.itemid
        substance_ids = self.db.execute(select)
        # Continue here
        for sid, concentration_min, concentration_max in substance_ids:
            select = "SELECT title from substance WHERE substance_id = %s" %sid
            substance_title = self.db.execute(select)
            entry = {'title':substance_title, 'concentration_min':concentration_min, 'concentration_max':concentration_max}
            entry['resultstring'] = self.translate_recipes(entry)
            substances.append(entry)
        #self.db.close()
        return substances

    def translate_recipes(self, recipe):
        resultstring = "%s (%s %s %s, %s %s %s)" % (recipe['title'][0][0], ">=", recipe['concentration_min'], "%", "<=", recipe['concentration_max'], "%")
        return resultstring

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value

    def get_none_translation(self, value):
        if value == None or value == 'None':
            return ''
        else:
            return value

    def usecase_translation(self, value):
        vocabulary = get_vocabulary('usecases')
        newlist = list()
        try:
            for v in value:
                for i in vocabulary:
                    if i[0] == v:
                        newlist.append(i[1])
            result = ', '.join(newlist)
        except:
            result = ''
        return result

    def new_usecase_translation(self):
        usecases = []
        select = "SELECT usecase_id from usecasepairs WHERE mixture_id = %s" % self.itemid
        usecaseids = self.db.execute(select)
        # Continue here

        for ucid in usecaseids:
            select = "SELECT usecase_name from usecases WHERE usecase_id = %s" % ucid
            usecase_title = self.db.execute(select)
            entry = {'title': usecase_title}
            usecases.append(entry)
        # self.db.close()
        return usecases

    def new_usecase_translation2(self, id):
        usecases = []
        select = "SELECT usecase_id from usecasepairs WHERE mixture_id = %s" % id
        usecaseids = self.db.execute(select)
        # Continue here

        for ucid in usecaseids:
            select = "SELECT usecase_name from usecases WHERE usecase_id = %s" % ucid
            usecase_title = self.db.execute(select)
            entry = {'title': usecase_title}
            usecases.append(entry)
        # self.db.close()
        return usecases

    def translate_usecases(self, usecases):
        resultstring = ""
        index = 0
        for i in usecases:
            resultstring = resultstring + "%s, " % (usecases[index]['title'][0][0])
            index = index + 1
        resultstring = resultstring[:-2]
        return resultstring

    def new_usecases_translation(self):
        usecases = []
        select = "SELECT usecase_id from usecasepairs WHERE mixture_id = %s" % self.itemid
        caseids = self.db.execute(select)
        # Continue here

        for caseid in caseids:
            select = "SELECT usecase_name from usecases WHERE usecase_id = %s" % caseid
            case_title = self.db.execute(select)
            entry = {'title': case_title}
            usecases.append(entry)
        # self.db.close()
        return usecases

    def new_application_areas_translation(self):
        applicationareas = []
        select = "SELECT area_id from areapairs WHERE mixture_id = %s" % self.itemid
        areaids = self.db.execute(select)
        # Continue here

        for arid in areaids:
            select = "SELECT application_area_name from application_areas WHERE application_area_id = %s" % arid
            area_title = self.db.execute(select)
            entry = {'title': area_title}
            applicationareas.append(entry)
        # self.db.close()
        return applicationareas

    def new_application_areas_translation2(self, id):
        applicationareas = []
        select = "SELECT area_id from areapairs WHERE mixture_id = %s" % id
        areaids = self.db.execute(select)
        # Continue here

        for arid in areaids:
            select = "SELECT application_area_name from application_areas WHERE application_area_id = %s" % arid
            area_title = self.db.execute(select)
            entry = {'title': area_title}
            applicationareas.append(entry)
        # self.db.close()
        return applicationareas

    def translate_application_areas(self, areas):
        resultstring = ""
        index = 0
        for i in areas:
            resultstring = resultstring + "%s, " % (areas[index]['title'][0][0])
            index = index + 1
        resultstring = resultstring[:-2]
        return resultstring

    def application_areas_translation(self, value):
        vocabulary = get_vocabulary('application_areas')
        newlist = list()
        try:
            for v in value:
                for i in vocabulary:
                    if i[0] == v:
                        newlist.append(i[1])
            result = ', '.join(newlist)
        except:
            result = ''
        return result

    def unbundle_list(self, value):
        if value:
            result = value.split('@')
        else:
            result = list()
        return result

    def getRightUrl(self, value):
        urlels = value.split('=')
        if len(urlels[1]) < 6:
            param = urlels[1].zfill(6)
            return urlels[0] + '=' + param
        return value
