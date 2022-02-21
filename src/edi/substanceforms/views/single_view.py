# -*- coding: utf-8 -*-
from edi.substanceforms import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
from edi.substanceforms.config import editrole
from edi.substanceforms.helpers import get_vocabulary
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import psycopg2


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
            key_value_pair = getattr(self, key, None)

            if key_value_pair:
                entry = key_value_pair()
                if entry:
                    title = entry['title']
                    value = entry['value']
                    fragment = f'<dt class="col col-sm-5">{title}</dt><dd class="col col-sm-7">{value}</dd><div class="w-100 divider"></div>'
                    fragments.append(fragment)

        return fragments

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
        value = self.get_attr_translation('substance_types_new', self.article[5])
        if value:
            return {'title': title, 'value': value}
        return {}

    def branch(self):
        title = "Branche"
        if self.context.tablename == 'substance_mixture':
            value = self.get_attr_translation('branchen', self.article[4])
        elif self.context.tablename == 'substance':
            value = self.get_attr_translation('branchen', self.article[8])
        if value:
            return {'title': title, 'value': value}
        return {}

    def manufacturer_id(self):
        title = "Hersteller"
        if self.context.tablename == 'substance_mixture':
            value = self.get_manufacturer(self.article[25])
            import pdb; pdb.set_trace()
        elif self.context.tablename == 'spray_powder':
            value = self.get_manufacturer(self.article[11])
        elif self.context.tablename == 'manufacturer':
            value = False
        if value:
            return {'title': title, 'value': value}
        return {}

    def skin_category(self):
        title = "Hautschutzmittelgruppe"
        if self.context.tablename == 'substance_mixture':
            value = self.get_attr_translation('hskategorie', self.article[16])
        elif self.context.tablename == 'substance':
            value = self.get_attr_translation('hskategorie', self.article[7])
        if value:
            return {'title': title, 'value': value}
        return {}

    def checked_emissions(self):
        title = "Emissionsarmes Produkt"
        if self.context.tablename == 'substance_mixture':
            value = self.get_attr_translation('boolvocab', str(self.article[17]))
        elif self.context.tablename == 'spray_powder':
            value = self.get_attr_translation('boolvocab', str(self.article[8]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_150(self):
        title = "Verdampfungsfaktor 150 Grad"
        value = self.article[10]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_160(self):
        title = "Verdampfungsfaktor 160 Grad"
        value = self.article[11]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_170(self):
        title = "Verdampfungsfaktor 170 Grad"
        value = self.article[12]
        if value:
            return {'title': title, 'value': value}
        return {}

    def evaporation_lane_180(self):
        title = "Verdampfungsfaktor 180 Grad"
        value = self.article[13]
        if value:
            return {'title': title, 'value': value}
        return {}

    def date_checked(self):
        title = "Prüfdatum"
        if self.context.tablename == 'substance_mixture':
            value = self.article[18]
        elif self.context.tablename == 'spray_powder':
            value = self.article[9]
        if value:
            return {'title': title, 'value': value}
        return {}

    def flashpoint(self):
        title = "Flammpunkt in °C"
        value = self.article[19]
        if value:
            return {'title': title, 'value': value}
        return {}

    def ueg(self):
        title = "UEG in g/m3"
        value = self.article[14]
        if value:
            return {'title': title, 'value': value}
        return {}

    def response(self):
        title = "Responsefaktor"
        value = self.article[15]
        if value:
            return {'title': title, 'value': value}
        return {}

    def application_areas(self):
        title = "Anwendungsgebiete"
        value = self.translate_application_areas(self.new_application_areas_translation2(self.article[0]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def usecases(self):
        title = "Verwendungszwecke"
        value = self.translate_usecases(self.new_usecase_translation2(self.article[0]))
        if value:
            return {'title': title, 'value': value}
        return {}

    def concentration(self):
        title = "Konzentration in wässriger Lösung"
        value = self.article[6]
        if value:
            return {'title': title, 'value': value}
        return {}

    def casnr(self):
        title = "CAS-Nummer"
        value = self.article[4]
        if value:
            return {'title': title, 'value': value}
        return {}

    def egnr(self):
        title = "EG-Nummer"
        value = self.article[5]
        if value:
            return {'title': title, 'value': value}
        return {}

    def dnel_lokal(self):
        title = "DNEL Inhalation [mg/m3]: lokal"
        value = self.article[9]
        if value:
            return {'title': title, 'value': value}
        return {}

    def dnel_systemisch(self):
        title = "DNEL Inhalation [mg/m3]: systemisch"
        value = self.article[10]
        if value:
            return {'title': title, 'value': value}
        return {}

    def homepage(self):
        title = "Homepage"
        value = self.article[4]
        if value:
            return {'title': title, 'value': value}
        return {}

    def product_class(self):
        title = "Produktklasse"
        value = self.article[4]
        if value:
            return {'title': title, 'value': value}
        return {}

    def starting_material(self):
        title = "Ausgangsmaterial"
        value = self.article[5]
        if value:
            return {'title': title, 'value': value}
        return {}

    def volume_share(self):
        title = "Volumenanteil"
        value = self.article[7]
        if value:
            return {'title': title, 'value': value}
        return {}

    def median_share(self):
        title = "Medianwert"
        value = self.article[6]
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
