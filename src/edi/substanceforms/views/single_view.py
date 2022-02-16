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
        if self.context.tablename == 'substance_mixture':
            #self.machines = self.get_machines()
            #self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('substance_mixture_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        if self.context.tablename == 'substance':
            #self.machines = self.get_machines()
            #self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('substance_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'spray_powder':
            template = ViewPageTemplateFile('spray_powder_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'manufacturer':
            template = ViewPageTemplateFile('manufacturer_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        return self.index()

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
